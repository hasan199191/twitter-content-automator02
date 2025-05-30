"""
Configuration management for the Twitter Bot.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class for managing all bot settings."""
    
    def __init__(self):
        # API Keys and Credentials
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
        self.TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
        self.TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
        self.TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
        
        # Bot Configuration
        self.POST_INTERVAL_HOURS = int(os.getenv("POST_INTERVAL_HOURS", "4"))
        self.MAX_POSTS_PER_DAY = int(os.getenv("MAX_POSTS_PER_DAY", "6"))
        self.CONTENT_MIN_LENGTH = int(os.getenv("CONTENT_MIN_LENGTH", "100"))
        self.CONTENT_MAX_LENGTH = int(os.getenv("CONTENT_MAX_LENGTH", "280"))
        
        # Database Configuration
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", "twitter_bot.db")
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "twitter_bot.log")
        
        # Content Generation Settings
        self.CONTENT_TEMPERATURE = float(os.getenv("CONTENT_TEMPERATURE", "0.7"))
        self.AVOID_RECENT_POSTS_DAYS = int(os.getenv("AVOID_RECENT_POSTS_DAYS", "7"))
        
        # Web Interface
        self.WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
        self.WEB_PORT = int(os.getenv("WEB_PORT", "5000"))
        
    def validate(self):
        """Validate that all required configuration is present."""
        required_vars = [
            ("GEMINI_API_KEY", self.GEMINI_API_KEY),
            ("TWITTER_API_KEY", self.TWITTER_API_KEY),
            ("TWITTER_API_SECRET", self.TWITTER_API_SECRET),
            ("TWITTER_ACCESS_TOKEN", self.TWITTER_ACCESS_TOKEN),
            ("TWITTER_ACCESS_TOKEN_SECRET", self.TWITTER_ACCESS_TOKEN_SECRET),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
                
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        return True
