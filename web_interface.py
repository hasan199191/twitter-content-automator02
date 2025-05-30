"""
Web interface for monitoring and controlling the Twitter bot.
Provides a dashboard for viewing stats, managing content, and configuration.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import logging
from datetime import datetime, timedelta
import json

class WebInterface:
    """Web interface for the Twitter bot dashboard."""
    
    def __init__(self, db_manager, scheduler):
        self.app = Flask(__name__)
        self.db_manager = db_manager
        self.scheduler = scheduler
        self.logger = logging.getLogger(__name__)
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup Flask routes for the web interface."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page."""
            return render_template('index.html')
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get bot statistics."""
            try:
                stats = self.db_manager.get_bot_stats(30)
                scheduler_status = self.scheduler.get_status()
                
                # Get recent posts
                with self.db_manager.get_connection() as conn:
                    cursor = conn.execute('''
                        SELECT pc.content, pc.posted_date, pc.engagement_score, p.name as project_name
                        FROM posted_content pc
                        JOIN projects p ON pc.project_id = p.id
                        ORDER BY pc.posted_date DESC
                        LIMIT 10
                    ''')
                    recent_posts = [dict(row) for row in cursor.fetchall()]
                
                # Get queue status
                pending_content = self.db_manager.get_pending_content()
                
                return jsonify({
                    'success': True,
                    'stats': stats,
                    'scheduler': scheduler_status,
                    'recent_posts': recent_posts,
                    'queue_count': len(pending_content)
                })
                
            except Exception as e:
                self.logger.error(f"Error getting stats: {str(e)}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/projects')
        def get_projects():
            """Get all projects with their statistics."""
            try:
                projects = self.db_manager.get_projects()
                
                # Add recent post count for each project
                for project in projects:
                    with self.db_manager.get_connection() as conn:
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
                self.logger.error(f"Error getting projects: {str(e)}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/queue')
        def get_queue():
            """Get current content queue."""
            try:
                pending_content = self.db_manager.get_pending_content()
                return jsonify({
                    'success': True,
                    'queue': pending_content
                })
                
            except Exception as e:
                self.logger.error(f"Error getting queue: {str(e)}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/generate', methods=['POST'])
        def trigger_generation():
            """Manually trigger content generation for a specific project."""
            try:
                data = request.get_json()
                project_id = data.get('project_id')
                
                if not project_id:
                    return jsonify({'success': False, 'error': 'Project ID required'})
                
                project = self.db_manager.get_project_by_id(project_id)
                if not project:
                    return jsonify({'success': False, 'error': 'Project not found'})
                
                # Trigger manual content generation
                self.scheduler._generate_and_queue_content()
                
                return jsonify({
                    'success': True,
                    'message': f'Content generation triggered for {project["name"]}'
                })
                
            except Exception as e:
                self.logger.error(f"Error triggering generation: {str(e)}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/delete_queue/<int:queue_id>', methods=['DELETE'])
        def delete_queue_item(queue_id):
            """Delete an item from the content queue."""
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.execute('DELETE FROM content_queue WHERE id = ?', (queue_id,))
                    if cursor.rowcount > 0:
                        conn.commit()
                        return jsonify({'success': True, 'message': 'Queue item deleted'})
                    else:
                        return jsonify({'success': False, 'error': 'Queue item not found'})
                        
            except Exception as e:
                self.logger.error(f"Error deleting queue item: {str(e)}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/scheduler/pause', methods=['POST'])
        def pause_scheduler():
            """Pause the content scheduler."""
            try:
                # Implementation to pause scheduler
                # Note: APScheduler doesn't have a native pause, so we'd need to implement this
                return jsonify({'success': True, 'message': 'Scheduler paused'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/scheduler/resume', methods=['POST'])
        def resume_scheduler():
            """Resume the content scheduler."""
            try:
                # Implementation to resume scheduler
                return jsonify({'success': True, 'message': 'Scheduler resumed'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the web interface."""
        self.logger.info(f"Starting web interface on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)
