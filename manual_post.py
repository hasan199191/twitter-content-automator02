#!/usr/bin/env python3
"""Manual content posting script for immediate testing"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append('.')

from twitter_client import TwitterClient
from database import DatabaseManager

def post_ready_content():
    """Post content that's ready to be published"""
    try:
        # Initialize components
        twitter_client = TwitterClient()
        db_manager = DatabaseManager()
        
        print("Checking for content ready to post...")
        
        # Get pending content
        pending_content = db_manager.get_pending_content()
        print(f"Found {len(pending_content)} pending items")
        
        if not pending_content:
            print("No content in queue")
            return
            
        # Post the first ready item
        content_item = pending_content[0]
        print(f"Posting content for {content_item['project_name']}...")
        print(f"Content preview: {content_item['content'][:100]}...")
        
        # Post to Twitter
        tweet_id = twitter_client.post_content(content_item['content'])
        
        if tweet_id:
            # Mark as posted
            db_manager.mark_content_posted(content_item['id'], tweet_id)
            print(f"✓ Successfully posted! Tweet ID: {tweet_id}")
            print(f"Check: https://twitter.com/JoiCryptoo/status/{tweet_id}")
        else:
            print("✗ Failed to post content")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    post_ready_content()