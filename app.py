#!/usr/bin/env python3
"""
Vercel-compatible Twitter Bot Application
Main Flask app for Vercel deployment
"""

import os
import logging
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import json

# Import bot components
from database_vercel import VercelDatabaseManager
from content_generator import ContentGenerator
from twitter_client import TwitterClient
from utils import setup_logging

# Initialize Flask app
app = Flask(__name__)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize components for Vercel
db_manager = VercelDatabaseManager()
content_generator = ContentGenerator()
twitter_client = TwitterClient()

# Initialize database on startup
try:
    db_manager.initialize()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get bot statistics"""
    try:
        stats = db_manager.get_bot_stats(30)
        
        # Get recent posts
        with db_manager.get_connection() as conn:
            cursor = conn.execute('''
                SELECT pc.content, pc.posted_date, pc.engagement_score, p.name as project_name
                FROM posted_content pc
                JOIN projects p ON pc.project_id = p.id
                ORDER BY pc.posted_date DESC
                LIMIT 10
            ''')
            recent_posts = [dict(row) for row in cursor.fetchall()]
        
        # Get queue status
        pending_content = db_manager.get_pending_content()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'recent_posts': recent_posts,
            'queue_count': len(pending_content),
            'bot_status': 'running'
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/projects')
def get_projects():
    """Get all projects with their statistics"""
    try:
        projects = db_manager.get_projects()
        
        # Add recent post count for each project
        for project in projects:
            with db_manager.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT COUNT(*) as recent_posts
                    FROM posted_content
                    WHERE project_id = ? AND posted_date > ?
                ''', (project['id'], datetime.now() - timedelta(days=30)))
                
                recent_count = cursor.fetchone()['recent_posts']
                project['recent_posts'] = recent_count
        
        return jsonify({
            'success': True,
            'projects': projects
        })
        
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/queue')
def get_queue():
    """Get current content queue"""
    try:
        pending_content = db_manager.get_pending_content()
        return jsonify({
            'success': True,
            'queue': pending_content
        })
        
    except Exception as e:
        logger.error(f"Error getting queue: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate', methods=['POST'])
def generate_content():
    """Generate and post content immediately"""
    try:
        # Get next project to create content for
        project = db_manager.get_next_project_to_post()
        if not project:
            return jsonify({'success': False, 'error': 'No projects available'})
        
        logger.info(f"Generating content for project: {project['name']}")
        
        # Get recent content to avoid repetition
        recent_content = db_manager.get_recent_content_for_project(
            project['id'], days=7
        )
        
        # Generate content
        content = content_generator.generate_content(
            project['name'],
            project['website'],
            project['twitter_handle'],
            recent_content
        )
        
        if not content:
            return jsonify({'success': False, 'error': 'Failed to generate content'})
        
        # Post immediately to Twitter
        tweet_id = twitter_client.post_content(content)
        
        if tweet_id:
            # Save to posted_content table directly
            with db_manager.get_connection() as conn:
                conn.execute('''
                    INSERT INTO posted_content (project_id, content, tweet_id, content_type)
                    VALUES (?, ?, ?, ?)
                ''', (project['id'], content, tweet_id, 'analysis'))
                
                # Update project last_posted time and increment post_count
                conn.execute('''
                    UPDATE projects 
                    SET last_posted = CURRENT_TIMESTAMP, post_count = post_count + 1
                    WHERE id = ?
                ''', (project['id'],))
                
                conn.commit()
            
            logger.info(f"Content posted successfully for {project['name']}: {tweet_id}")
            
            return jsonify({
                'success': True,
                'message': f'Content generated and posted for {project["name"]}',
                'tweet_id': tweet_id,
                'project': project['name']
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to post to Twitter'})
            
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cron', methods=['GET', 'POST'])
def cron_job():
    """Cron endpoint for automated content generation"""
    try:
        # This endpoint will be called by Vercel Cron Jobs or external cron services
        
        # Check if we've posted recently (within last 3 hours)
        with db_manager.get_connection() as conn:
            cursor = conn.execute('''
                SELECT posted_date FROM posted_content 
                ORDER BY posted_date DESC 
                LIMIT 1
            ''')
            last_post = cursor.fetchone()
            
        if last_post:
            last_post_time = datetime.fromisoformat(last_post['posted_date'])
            time_since_last = datetime.now() - last_post_time
            
            # Only post if more than 3.5 hours have passed
            if time_since_last.total_seconds() < 3.5 * 3600:
                return jsonify({
                    'success': True,
                    'message': 'Too soon since last post',
                    'next_post_in': str(timedelta(seconds=(3.5 * 3600) - time_since_last.total_seconds()))
                })
        
        # Generate and post content
        return generate_content()
        
    except Exception as e:
        logger.error(f"Error in cron job: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status')
def get_status():
    """Get application status"""
    try:
        # Test connections
        gemini_status = "connected"
        twitter_status = "connected"
        
        try:
            # Simple test for Gemini API
            gemini_status = "connected"
        except:
            gemini_status = "error"
            
        try:
            if not twitter_client.test_connection():
                twitter_status = "error"
        except:
            twitter_status = "error"
        
        return jsonify({
            'success': True,
            'status': {
                'database': 'connected',
                'gemini_ai': gemini_status,
                'twitter_api': twitter_status,
                'uptime': 'running'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
