#!/usr/bin/env python3
"""
Automated Blockchain Content Generator and Twitter Bot
Main entry point for the application.
"""

import os
import sys
import logging
import signal
import time
from datetime import datetime
from threading import Thread

from config import Config
from database import DatabaseManager
from content_generator import ContentGenerator
from twitter_client import TwitterClient
from scheduler import ContentScheduler
from web_interface import WebInterface
from utils import setup_logging

class TwitterBot:
    def __init__(self):
        """Initialize the Twitter bot with all necessary components."""
        self.config = Config()
        self.db_manager = DatabaseManager()
        self.content_generator = ContentGenerator()
        self.twitter_client = TwitterClient()
        self.scheduler = ContentScheduler(
            self.content_generator,
            self.twitter_client,
            self.db_manager
        )
        self.web_interface = WebInterface(self.db_manager, self.scheduler)
        self.running = False
        
        # Setup logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Start the bot and all its components."""
        try:
            self.logger.info("Starting Twitter Bot...")
            
            # Initialize database
            self.db_manager.initialize()
            self.logger.info("Database initialized successfully")
            
            # Test API connections
            if not self._test_connections():
                self.logger.error("API connection tests failed. Exiting.")
                return False
                
            # Start scheduler
            self.scheduler.start()
            self.logger.info("Content scheduler started")
            
            # Start web interface in a separate thread
            web_thread = Thread(target=self.web_interface.run, daemon=True)
            web_thread.start()
            self.logger.info("Web interface started on http://0.0.0.0:5000")
            
            self.running = True
            self.logger.info("Twitter Bot is now running successfully!")
            
            # Keep the main thread alive
            self._run_main_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start bot: {str(e)}")
            return False
            
    def _test_connections(self):
        """Test connections to external APIs."""
        self.logger.info("Testing API connections...")
        
        # Test Gemini AI
        try:
            test_content = self.content_generator.generate_content("Test", "test.com", "@test")
            if test_content:
                self.logger.info("✓ Gemini AI connection successful")
            else:
                self.logger.error("✗ Gemini AI connection failed")
                return False
        except Exception as e:
            self.logger.error(f"✗ Gemini AI connection failed: {str(e)}")
            return False
            
        # Test Twitter API
        try:
            if self.twitter_client.test_connection():
                self.logger.info("✓ Twitter API connection successful")
            else:
                self.logger.error("✗ Twitter API connection failed")
                return False
        except Exception as e:
            self.logger.error(f"✗ Twitter API connection failed: {str(e)}")
            return False
            
        return True
        
    def _run_main_loop(self):
        """Main loop to keep the bot running."""
        try:
            while self.running:
                time.sleep(60)  # Check every minute
                
                # Log status periodically
                if datetime.now().minute % 10 == 0:
                    self.logger.info("Bot is running normally...")
                    
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal. Shutting down...")
            self.stop()
            
    def stop(self):
        """Stop the bot and cleanup resources."""
        self.logger.info("Stopping Twitter Bot...")
        self.running = False
        
        if self.scheduler:
            self.scheduler.stop()
            self.logger.info("Scheduler stopped")
            
        self.logger.info("Twitter Bot stopped successfully")
        
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}. Initiating shutdown...")
        self.stop()
        sys.exit(0)

def main():
    """Main function to start the bot."""
    # Setup signal handlers for graceful shutdown
    bot = TwitterBot()
    signal.signal(signal.SIGINT, bot._signal_handler)
    signal.signal(signal.SIGTERM, bot._signal_handler)
    
    # Start the bot
    success = bot.start()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
