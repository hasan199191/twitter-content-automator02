"""
Database management for the Twitter Bot.
Handles project data, content history, and posting schedules.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

class DatabaseManager:
    """Manages SQLite database operations for the Twitter bot."""
    
    def __init__(self, db_path: str = "twitter_bot.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
            
    def initialize(self):
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            # Projects table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    website TEXT NOT NULL,
                    twitter_handle TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_posted TIMESTAMP,
                    post_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Posted content table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS posted_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    content TEXT NOT NULL,
                    tweet_id TEXT,
                    posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    engagement_score INTEGER DEFAULT 0,
                    content_type TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            # Content queue table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    content TEXT NOT NULL,
                    content_type TEXT DEFAULT 'analysis',
                    scheduled_time TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            # Bot statistics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE,
                    posts_generated INTEGER DEFAULT 0,
                    posts_published INTEGER DEFAULT 0,
                    errors_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            self.logger.info("Database initialized successfully")
            
        # Initialize with project data
        self._populate_projects()
        
    def _populate_projects(self):
        """Populate the projects table with initial data."""
        from projects_data import BLOCKCHAIN_PROJECTS
        
        with self.get_connection() as conn:
            for project in BLOCKCHAIN_PROJECTS:
                try:
                    conn.execute('''
                        INSERT OR IGNORE INTO projects (name, website, twitter_handle, description, category)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        project['name'],
                        project['website'],
                        project['twitter_handle'],
                        project.get('description', ''),
                        project.get('category', 'DeFi')
                    ))
                except Exception as e:
                    self.logger.error(f"Error inserting project {project['name']}: {str(e)}")
                    
            conn.commit()
            self.logger.info("Projects data populated successfully")
            
    def get_projects(self, active_only: bool = True) -> List[Dict]:
        """Get all projects from the database."""
        with self.get_connection() as conn:
            query = "SELECT * FROM projects"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY last_posted ASC NULLS FIRST"
            
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]
            
    def get_project_by_id(self, project_id: int) -> Optional[Dict]:
        """Get a specific project by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
            
    def get_next_project_to_post(self) -> Optional[Dict]:
        """Get the next project that should have content generated."""
        with self.get_connection() as conn:
            # Get project that hasn't been posted recently
            cutoff_time = datetime.now() - timedelta(days=1)
            cursor = conn.execute('''
                SELECT * FROM projects 
                WHERE is_active = 1 
                AND (last_posted IS NULL OR last_posted < ?)
                ORDER BY last_posted ASC NULLS FIRST
                LIMIT 1
            ''', (cutoff_time,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
    def save_generated_content(self, project_id: int, content: str, content_type: str = "analysis") -> int:
        """Save generated content to the queue."""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO content_queue (project_id, content, content_type, scheduled_time)
                VALUES (?, ?, ?, ?)
            ''', (project_id, content, content_type, datetime.now()))
            
            conn.commit()
            return cursor.lastrowid
            
    def get_pending_content(self) -> List[Dict]:
        """Get content ready to be posted."""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT cq.*, p.name as project_name, p.twitter_handle
                FROM content_queue cq
                JOIN projects p ON cq.project_id = p.id
                WHERE cq.status = 'pending'
                AND cq.scheduled_time <= ?
                ORDER BY cq.scheduled_time ASC
            ''', (datetime.now(),))
            
            return [dict(row) for row in cursor.fetchall()]
            
    def mark_content_posted(self, queue_id: int, tweet_id: str):
        """Mark content as posted and move to posted_content table."""
        with self.get_connection() as conn:
            # Get the queued content
            cursor = conn.execute("SELECT * FROM content_queue WHERE id = ?", (queue_id,))
            queued_content = cursor.fetchone()
            
            if queued_content:
                # Insert into posted_content
                conn.execute('''
                    INSERT INTO posted_content (project_id, content, tweet_id, content_type)
                    VALUES (?, ?, ?, ?)
                ''', (
                    queued_content['project_id'],
                    queued_content['content'],
                    tweet_id,
                    queued_content['content_type']
                ))
                
                # Update project last_posted time and increment post_count
                conn.execute('''
                    UPDATE projects 
                    SET last_posted = CURRENT_TIMESTAMP, post_count = post_count + 1
                    WHERE id = ?
                ''', (queued_content['project_id'],))
                
                # Remove from queue
                conn.execute("DELETE FROM content_queue WHERE id = ?", (queue_id,))
                
                conn.commit()
                self.logger.info(f"Content marked as posted: tweet_id={tweet_id}")
                
    def get_recent_content_for_project(self, project_id: int, days: int = 7) -> List[str]:
        """Get recent content for a project to avoid duplicates."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT content FROM posted_content
                WHERE project_id = ? AND posted_date > ?
                ORDER BY posted_date DESC
            ''', (project_id, cutoff_date))
            
            return [row['content'] for row in cursor.fetchall()]
            
    def get_bot_stats(self, days: int = 30) -> Dict:
        """Get bot statistics for the specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_connection() as conn:
            # Total posts
            cursor = conn.execute('''
                SELECT COUNT(*) as total_posts FROM posted_content
                WHERE posted_date > ?
            ''', (cutoff_date,))
            total_posts = cursor.fetchone()['total_posts']
            
            # Posts by project
            cursor = conn.execute('''
                SELECT p.name, COUNT(*) as post_count
                FROM posted_content pc
                JOIN projects p ON pc.project_id = p.id
                WHERE pc.posted_date > ?
                GROUP BY p.name
                ORDER BY post_count DESC
            ''', (cutoff_date,))
            posts_by_project = [dict(row) for row in cursor.fetchall()]
            
            # Daily stats
            cursor = conn.execute('''
                SELECT DATE(posted_date) as date, COUNT(*) as posts
                FROM posted_content
                WHERE posted_date > ?
                GROUP BY DATE(posted_date)
                ORDER BY date DESC
            ''', (cutoff_date,))
            daily_posts = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_posts': total_posts,
                'posts_by_project': posts_by_project,
                'daily_posts': daily_posts,
                'period_days': days
            }
            
    def update_daily_stats(self, posts_generated: int = 0, posts_published: int = 0, errors_count: int = 0):
        """Update daily statistics."""
        today = datetime.now().date()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO bot_stats 
                (date, posts_generated, posts_published, errors_count, last_updated)
                VALUES (?, 
                    COALESCE((SELECT posts_generated FROM bot_stats WHERE date = ?), 0) + ?,
                    COALESCE((SELECT posts_published FROM bot_stats WHERE date = ?), 0) + ?,
                    COALESCE((SELECT errors_count FROM bot_stats WHERE date = ?), 0) + ?,
                    CURRENT_TIMESTAMP)
            ''', (today, today, posts_generated, today, posts_published, today, errors_count))
            
            conn.commit()
