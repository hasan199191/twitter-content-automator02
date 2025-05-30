"""
Vercel-compatible database management for the Twitter Bot.
Uses environment-based storage instead of local SQLite files.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from projects_data import BLOCKCHAIN_PROJECTS

class VercelDatabaseManager:
    """Manages database operations for Vercel deployment using environment variables"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.projects = BLOCKCHAIN_PROJECTS
        
    def initialize(self):
        """Initialize the database - for Vercel, this just ensures projects are available"""
        self.logger.info("Database initialized successfully (Vercel mode)")
        
    def get_projects(self, active_only: bool = True) -> List[Dict]:
        """Get all projects from the projects data"""
        projects_with_stats = []
        
        for i, project in enumerate(self.projects):
            project_data = project.copy()
            project_data['id'] = i + 1
            project_data['post_count'] = 0
            project_data['last_posted'] = None
            project_data['is_active'] = 1
            projects_with_stats.append(project_data)
            
        return projects_with_stats
        
    def get_project_by_id(self, project_id: int) -> Optional[Dict]:
        """Get a specific project by ID"""
        if 1 <= project_id <= len(self.projects):
            project = self.projects[project_id - 1].copy()
            project['id'] = project_id
            project['post_count'] = 0
            project['last_posted'] = None
            project['is_active'] = 1
            return project
        return None
        
    def get_next_project_to_post(self) -> Optional[Dict]:
        """Get the next project that should have content generated"""
        # For Vercel, we'll rotate through projects based on current time
        import random
        project_index = random.randint(0, len(self.projects) - 1)
        
        project = self.projects[project_index].copy()
        project['id'] = project_index + 1
        project['post_count'] = 0
        project['last_posted'] = None
        project['is_active'] = 1
        
        return project
        
    def save_generated_content(self, project_id: int, content: str, content_type: str = "analysis") -> int:
        """Save generated content - for Vercel, we'll return a mock ID"""
        self.logger.info(f"Content generated for project {project_id}: {len(content)} characters")
        return 1
        
    def get_pending_content(self) -> List[Dict]:
        """Get content ready to be posted - for Vercel, returns empty as we post immediately"""
        return []
        
    def mark_content_posted(self, queue_id: int, tweet_id: str):
        """Mark content as posted"""
        self.logger.info(f"Content marked as posted: tweet_id={tweet_id}")
        
    def get_recent_content_for_project(self, project_id: int, days: int = 7) -> List[str]:
        """Get recent content for a project to avoid duplicates"""
        # For Vercel, return empty to allow content generation
        return []
        
    def get_bot_stats(self, days: int = 30) -> Dict:
        """Get bot statistics"""
        return {
            'total_posts': 0,
            'posts_by_project': [],
            'daily_posts': [],
            'period_days': days
        }
        
    def update_daily_stats(self, posts_generated: int = 0, posts_published: int = 0, errors_count: int = 0):
        """Update daily statistics"""
        self.logger.info(f"Stats updated: generated={posts_generated}, published={posts_published}, errors={errors_count}")
        
    def get_connection(self):
        """Mock connection for compatibility"""
        class MockConnection:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def execute(self, *args):
                return self
            def fetchall(self):
                return []
            def fetchone(self):
                return None
            def commit(self):
                pass
                
        return MockConnection()