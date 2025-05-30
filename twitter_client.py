"""
Twitter API client for posting content.
Handles authentication and tweet posting with error handling.
"""

import tweepy
import logging
import time
import re
from typing import Optional, Dict
from datetime import datetime

class TwitterClient:
    """Manages Twitter API interactions for posting content."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.api = None
        self._initialize_twitter_client()
        
    def _initialize_twitter_client(self):
        """Initialize Twitter API client with credentials."""
        import os
        
        # Get credentials from environment
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        if not all([api_key, api_secret, access_token, access_token_secret]):
            raise ValueError("Missing required Twitter API credentials")
            
        try:
            # Initialize v2 client for posting
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Initialize v1.1 API for additional features if needed
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret, access_token, access_token_secret
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            self.logger.info("Twitter API client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter client: {str(e)}")
            raise
            
    def test_connection(self) -> bool:
        """Test the Twitter API connection."""
        try:
            # Test by getting user information
            user = self.client.get_me()
            if user and user.data:
                self.logger.info(f"Twitter connection test successful. User: @{user.data.username}")
                return True
            else:
                self.logger.error("Twitter connection test failed: No user data returned")
                return False
                
        except Exception as e:
            self.logger.error(f"Twitter connection test failed: {str(e)}")
            return False
            
    def post_tweet(self, content: str) -> Optional[str]:
        """Post a single tweet and return the tweet ID."""
        try:
            # Clean and validate content
            content = content.strip()
            if len(content) > 280:
                self.logger.warning(f"Tweet content too long ({len(content)} chars), truncating")
                content = content[:277] + "..."
                
            if len(content) < 10:
                self.logger.error("Tweet content too short")
                return None
                
            # Post the tweet
            response = self.client.create_tweet(text=content)
            
            if response and response.data:
                tweet_id = response.data['id']
                self.logger.info(f"Tweet posted successfully: ID {tweet_id}")
                return str(tweet_id)
            else:
                self.logger.error("Failed to post tweet: No response data")
                return None
                
        except tweepy.Forbidden as e:
            self.logger.error(f"Twitter API forbidden error: {str(e)}")
            return None
        except tweepy.TooManyRequests as e:
            self.logger.error(f"Twitter API rate limit exceeded: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error posting tweet: {str(e)}")
            return None
            
    def post_thread(self, tweets: list) -> Optional[list]:
        """Post a thread of tweets and return list of tweet IDs."""
        if not tweets:
            return None
            
        tweet_ids = []
        previous_tweet_id = None
        
        try:
            for i, tweet_content in enumerate(tweets):
                tweet_content = tweet_content.strip()
                
                # Validate tweet content
                if len(tweet_content) > 280:
                    tweet_content = tweet_content[:277] + "..."
                    
                if len(tweet_content) < 10:
                    self.logger.warning(f"Skipping tweet {i+1} - too short")
                    continue
                    
                # Post tweet (reply to previous if it's part of a thread)
                if previous_tweet_id:
                    response = self.client.create_tweet(
                        text=tweet_content,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                else:
                    response = self.client.create_tweet(text=tweet_content)
                    
                if response and response.data:
                    tweet_id = str(response.data['id'])
                    tweet_ids.append(tweet_id)
                    previous_tweet_id = tweet_id
                    self.logger.info(f"Thread tweet {i+1} posted: ID {tweet_id}")
                    
                    # Small delay between tweets to avoid rate limiting
                    if i < len(tweets) - 1:
                        time.sleep(2)
                else:
                    self.logger.error(f"Failed to post thread tweet {i+1}")
                    break
                    
            if tweet_ids:
                self.logger.info(f"Thread posted successfully: {len(tweet_ids)} tweets")
                return tweet_ids
            else:
                self.logger.error("Failed to post thread: No tweets posted")
                return None
                
        except Exception as e:
            self.logger.error(f"Error posting thread: {str(e)}")
            return tweet_ids if tweet_ids else None
            
    def post_content(self, content: str) -> Optional[str]:
        """Post content (single tweet or thread) and return primary tweet ID."""
        try:
            # Determine if content is a thread (contains numbered tweets or multiple paragraphs)
            if self._is_thread_content(content):
                tweets = self._parse_thread_content(content)
                tweet_ids = self.post_thread(tweets)
                return tweet_ids[0] if tweet_ids else None
            else:
                return self.post_tweet(content)
                
        except Exception as e:
            self.logger.error(f"Error posting content: {str(e)}")
            return None
            
    def _is_thread_content(self, content: str) -> bool:
        """Determine if content should be posted as a thread."""
        # Check for numbered tweets (1/3, 2/3, etc.)
        if "/" in content and any(char.isdigit() for char in content.split("/")[0][-3:]):
            return True
            
        # Check for multiple distinct paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            return True
            
        # Check for thread emoji
        if "🧵" in content:
            return True
            
        return False
        
    def _parse_thread_content(self, content: str) -> list:
        """Parse thread content into individual tweets."""
        tweets = []
        
        # Split by double newlines first
        parts = content.split('\n\n')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Remove thread numbering if present (1/3, 2/3, etc.)
            # Keep the content but clean up the numbering
            cleaned_part = re.sub(r'^\d+/\d+\s*', '', part)
            
            tweets.append(cleaned_part)
            
        return tweets
        
    def get_tweet_stats(self, tweet_id: str) -> Optional[Dict]:
        """Get statistics for a posted tweet."""
        try:
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['public_metrics', 'created_at']
            )
            
            if tweet and tweet.data:
                metrics = tweet.data.public_metrics
                return {
                    'retweet_count': metrics.get('retweet_count', 0),
                    'like_count': metrics.get('like_count', 0),
                    'reply_count': metrics.get('reply_count', 0),
                    'quote_count': metrics.get('quote_count', 0),
                    'created_at': tweet.data.created_at
                }
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting tweet stats for {tweet_id}: {str(e)}")
            return None
