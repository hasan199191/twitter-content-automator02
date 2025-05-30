"""
Scheduling system for automated content generation and posting.
Manages timing, intervals, and posting limits.
"""

import logging
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from typing import Optional

class ContentScheduler:
    """Manages automated content generation and posting schedule."""
    
    def __init__(self, content_generator, twitter_client, db_manager):
        self.content_generator = content_generator
        self.twitter_client = twitter_client
        self.db_manager = db_manager
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.post_interval_hours = 3.5  # Posting interval 3.5 hours
        self.max_posts_per_day = 8  # Allow 8 posts per day for continuous operation
        self.daily_post_count = 0
        self.last_post_date = None
        
        # Setup scheduler jobs
        self._setup_scheduler_jobs()
        
    def _setup_scheduler_jobs(self):
        """Setup all scheduled jobs."""
        # Main content generation and posting job (3.5 hours = 210 minutes)
        self.scheduler.add_job(
            func=self._generate_and_queue_content,
            trigger=IntervalTrigger(minutes=210),
            id='content_generation',
            name='Generate Content',
            max_instances=1,
            replace_existing=True
        )
        
        # Content posting job (runs every 5 minutes to ensure immediate posting)
        self.scheduler.add_job(
            func=self._process_content_queue,
            trigger=IntervalTrigger(minutes=5),
            id='content_posting',
            name='Process Content Queue',
            max_instances=1,
            replace_existing=True
        )
        
        # Daily reset job (resets daily counters at midnight)
        self.scheduler.add_job(
            func=self._daily_reset,
            trigger=CronTrigger(hour=0, minute=0),
            id='daily_reset',
            name='Daily Reset',
            replace_existing=True
        )
        
        # Weekly maintenance job
        self.scheduler.add_job(
            func=self._weekly_maintenance,
            trigger=CronTrigger(day_of_week=0, hour=2, minute=0),  # Sunday 2 AM
            id='weekly_maintenance',
            name='Weekly Maintenance',
            replace_existing=True
        )
        
        self.logger.info("Scheduler jobs configured successfully")
        
    def start(self):
        """Start the scheduler."""
        try:
            self.scheduler.start()
            self.logger.info("Content scheduler started successfully")
            
            # Run initial content generation
            self._generate_and_queue_content()
            
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {str(e)}")
            raise
            
    def stop(self):
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown()
            self.logger.info("Content scheduler stopped")
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {str(e)}")
            
    def _generate_and_queue_content(self):
        """Generate content for the next project and queue it for immediate posting."""
        try:
            # Check daily limits
            if not self._can_post_today():
                self.logger.info("Daily posting limit reached. Skipping content generation.")
                return
                
            # Get next project to create content for
            project = self.db_manager.get_next_project_to_post()
            if not project:
                self.logger.warning("No projects available for content generation")
                return
                
            self.logger.info(f"Generating content for project: {project['name']}")
            
            # Get recent content to avoid repetition
            recent_content = self.db_manager.get_recent_content_for_project(
                project['id'], days=7
            )
            
            # Generate content
            content = self.content_generator.generate_content(
                project['name'],
                project['website'],
                project['twitter_handle'],
                recent_content
            )
            
            if content:
                # Schedule for immediate posting (within 1-5 minutes)
                posting_delay_minutes = random.randint(1, 5)
                scheduled_time = datetime.now() + timedelta(minutes=posting_delay_minutes)
                
                # Save to queue
                queue_id = self.db_manager.save_generated_content(
                    project['id'], 
                    content,
                    "analysis"
                )
                
                # Update scheduling time
                with self.db_manager.get_connection() as conn:
                    conn.execute(
                        "UPDATE content_queue SET scheduled_time = ? WHERE id = ?",
                        (scheduled_time, queue_id)
                    )
                    conn.commit()
                
                self.logger.info(f"Content queued for {project['name']}, scheduled for immediate posting at {scheduled_time}")
                
                # Update daily stats
                self.db_manager.update_daily_stats(posts_generated=1)
                
            else:
                self.logger.error(f"Failed to generate content for {project['name']}")
                self.db_manager.update_daily_stats(errors_count=1)
                
        except Exception as e:
            self.logger.error(f"Error in content generation job: {str(e)}")
            self.db_manager.update_daily_stats(errors_count=1)
            
    def _process_content_queue(self):
        """Process queued content and post to Twitter."""
        try:
            # Check daily limits
            if not self._can_post_today():
                self.logger.debug("Daily posting limit reached. Skipping queue processing.")
                return
                
            # Get pending content
            pending_content = self.db_manager.get_pending_content()
            
            if not pending_content:
                self.logger.debug("No pending content to post")
                return
                
            for content_item in pending_content:
                # Check if we can still post today
                if not self._can_post_today():
                    self.logger.info("Daily posting limit reached during queue processing")
                    break
                    
                # Post content
                self.logger.info(f"Posting content for {content_item['project_name']}")
                
                tweet_id = self.twitter_client.post_content(content_item['content'])
                
                if tweet_id:
                    # Mark as posted
                    self.db_manager.mark_content_posted(content_item['id'], tweet_id)
                    self._increment_daily_post_count()
                    
                    self.logger.info(f"Successfully posted content for {content_item['project_name']}: {tweet_id}")
                    
                    # Update daily stats
                    self.db_manager.update_daily_stats(posts_published=1)
                    
                    # Add delay between posts
                    import time
                    time.sleep(random.randint(60, 300))  # 1-5 minutes between posts
                    
                else:
                    self.logger.error(f"Failed to post content for {content_item['project_name']}")
                    self.db_manager.update_daily_stats(errors_count=1)
                    
        except Exception as e:
            self.logger.error(f"Error processing content queue: {str(e)}")
            self.db_manager.update_daily_stats(errors_count=1)
            
    def _can_post_today(self) -> bool:
        """Check if we can post more content today."""
        today = datetime.now().date()
        
        # Reset counter if it's a new day
        if self.last_post_date != today:
            self.daily_post_count = 0
            self.last_post_date = today
            
        return self.daily_post_count < self.max_posts_per_day
        
    def _increment_daily_post_count(self):
        """Increment the daily post counter."""
        today = datetime.now().date()
        if self.last_post_date != today:
            self.daily_post_count = 0
            self.last_post_date = today
            
        self.daily_post_count += 1
        
    def _daily_reset(self):
        """Reset daily counters and perform daily maintenance."""
        self.logger.info("Performing daily reset")
        self.daily_post_count = 0
        self.last_post_date = datetime.now().date()
        
        # Clean up old queue items (older than 24 hours and still pending)
        cutoff_time = datetime.now() - timedelta(hours=24)
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute('''
                DELETE FROM content_queue 
                WHERE status = 'pending' AND created_date < ?
            ''', (cutoff_time,))
            deleted_count = cursor.rowcount
            conn.commit()
            
        if deleted_count > 0:
            self.logger.info(f"Cleaned up {deleted_count} old queued items")
            
    def _weekly_maintenance(self):
        """Perform weekly maintenance tasks."""
        self.logger.info("Performing weekly maintenance")
        
        # Clean up old posted content (keep last 3 months)
        cutoff_date = datetime.now() - timedelta(days=90)
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute('''
                DELETE FROM posted_content WHERE posted_date < ?
            ''', (cutoff_date,))
            deleted_count = cursor.rowcount
            conn.commit()
            
        if deleted_count > 0:
            self.logger.info(f"Cleaned up {deleted_count} old posted content records")
            
        # Update engagement scores for recent tweets
        self._update_engagement_scores()
        
    def _update_engagement_scores(self):
        """Update engagement scores for recent tweets."""
        try:
            # Get recent tweets to update engagement
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT id, tweet_id FROM posted_content 
                    WHERE tweet_id IS NOT NULL 
                    AND posted_date > ? 
                    ORDER BY posted_date DESC LIMIT 50
                ''', (datetime.now() - timedelta(days=7),))
                
                recent_tweets = cursor.fetchall()
                
            updated_count = 0
            for tweet_record in recent_tweets:
                tweet_stats = self.twitter_client.get_tweet_stats(tweet_record['tweet_id'])
                if tweet_stats:
                    # Calculate engagement score
                    engagement_score = (
                        tweet_stats.get('like_count', 0) * 1 +
                        tweet_stats.get('retweet_count', 0) * 2 +
                        tweet_stats.get('reply_count', 0) * 3 +
                        tweet_stats.get('quote_count', 0) * 2
                    )
                    
                    # Update in database
                    with self.db_manager.get_connection() as conn:
                        conn.execute('''
                            UPDATE posted_content 
                            SET engagement_score = ? 
                            WHERE id = ?
                        ''', (engagement_score, tweet_record['id']))
                        conn.commit()
                        
                    updated_count += 1
                    
            if updated_count > 0:
                self.logger.info(f"Updated engagement scores for {updated_count} tweets")
                
        except Exception as e:
            self.logger.error(f"Error updating engagement scores: {str(e)}")
            
    def get_status(self) -> dict:
        """Get current scheduler status."""
        return {
            'running': self.scheduler.running,
            'daily_post_count': self.daily_post_count,
            'max_posts_per_day': self.max_posts_per_day,
            'can_post_today': self._can_post_today(),
            'last_post_date': self.last_post_date.isoformat() if self.last_post_date else None,
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ]
        }
