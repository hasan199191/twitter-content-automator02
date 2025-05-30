"""
Utility functions for the Twitter bot.
Includes logging setup, text processing, and helper functions.
"""

import logging
import os
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

def setup_logging():
    """Setup logging configuration for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    # log_file = os.getenv("LOG_FILE", "twitter_bot.log")  # Artık kullanılmayacak

    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Setup root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Reduce noise from external libraries
    logging.getLogger('tweepy').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove or replace problematic characters
    text = text.replace('\u2019', "'")  # Smart apostrophe
    text = text.replace('\u201c', '"')  # Smart quote left
    text = text.replace('\u201d', '"')  # Smart quote right
    text = text.replace('\u2013', '-')  # En dash
    text = text.replace('\u2014', '--') # Em dash
    
    return text

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text."""
    return re.findall(r'#\w+', text)

def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text."""
    return re.findall(r'@\w+', text)

def validate_tweet_length(text: str, max_length: int = 280) -> bool:
    """Validate if text fits within Twitter's character limit."""
    return len(text) <= max_length

def truncate_text_smart(text: str, max_length: int = 280, suffix: str = "...") -> str:
    """Intelligently truncate text to fit within character limit."""
    if len(text) <= max_length:
        return text
    
    # Try to cut at sentence boundary
    sentences = re.split(r'(?<=[.!?])\s+', text)
    truncated = ""
    
    for sentence in sentences:
        if len(truncated + " " + sentence + suffix) <= max_length:
            truncated += (" " + sentence) if truncated else sentence
        else:
            break
    
    if truncated:
        return truncated + suffix
    
    # Fall back to word boundary
    words = text.split()
    truncated = ""
    
    for word in words:
        if len(truncated + " " + word + suffix) <= max_length:
            truncated += (" " + word) if truncated else word
        else:
            break
    
    return truncated + suffix if truncated else text[:max_length-len(suffix)] + suffix

def generate_content_hash(content: str) -> str:
    """Generate a hash for content to check for duplicates."""
    # Normalize content for hashing
    normalized = re.sub(r'\s+', ' ', content.lower().strip())
    normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
    
    return hashlib.md5(normalized.encode()).hexdigest()

def is_similar_content(content1: str, content2: str, threshold: float = 0.7) -> bool:
    """Check if two pieces of content are similar."""
    # Simple similarity check based on common words
    words1 = set(re.findall(r'\w+', content1.lower()))
    words2 = set(re.findall(r'\w+', content2.lower()))
    
    if not words1 or not words2:
        return False
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    similarity = intersection / union if union > 0 else 0
    return similarity >= threshold

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display."""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def parse_thread_content(content: str) -> List[str]:
    """Parse content into thread format."""
    # Split by double newlines or thread indicators
    parts = re.split(r'\n\n|(?=\d+/\d+)', content)
    
    tweets = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Clean up thread numbering
        part = re.sub(r'^\d+/\d+\s*', '', part)
        
        # Validate length
        if len(part) > 280:
            part = truncate_text_smart(part, 280)
        
        if len(part) >= 10:  # Minimum length
            tweets.append(part)
    
    return tweets

def validate_project_data(project: Dict) -> bool:
    """Validate project data structure."""
    required_fields = ['name', 'website', 'twitter_handle']
    
    for field in required_fields:
        if field not in project or not project[field]:
            return False
    
    # Validate Twitter handle format
    twitter_handle = project['twitter_handle']
    if not twitter_handle.startswith('@') or len(twitter_handle) < 2:
        return False
    
    # Validate website format
    website = project['website']
    if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', website):
        return False
    
    return True

def calculate_engagement_score(metrics: Dict) -> int:
    """Calculate engagement score from tweet metrics."""
    return (
        metrics.get('like_count', 0) * 1 +
        metrics.get('retweet_count', 0) * 2 +
        metrics.get('reply_count', 0) * 3 +
        metrics.get('quote_count', 0) * 2
    )

def get_posting_time_suggestion() -> str:
    """Suggest optimal posting times based on current time."""
    current_hour = datetime.now().hour
    
    # Peak engagement times (general best practices)
    if 8 <= current_hour <= 10:
        return "Morning peak - good for professional content"
    elif 12 <= current_hour <= 14:
        return "Lunch time - high engagement period"
    elif 17 <= current_hour <= 19:
        return "Evening peak - excellent for engagement"
    elif 20 <= current_hour <= 22:
        return "Prime time - highest engagement potential"
    else:
        return "Off-peak hours - lower engagement expected"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations."""
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

class ContentValidator:
    """Validates content quality and compliance."""
    
    @staticmethod
    def validate_content_quality(content: str) -> Dict[str, bool]:
        """Validate content quality against various criteria."""
        results = {
            'length_ok': 50 <= len(content) <= 280,
            'has_substance': len(content.split()) >= 10,
            'not_all_caps': not content.isupper(),
            'no_spam_patterns': not re.search(r'(.)\1{5,}', content),
            'balanced_hashtags': len(extract_hashtags(content)) <= 3,
            'proper_mentions': len(extract_mentions(content)) <= 2
        }
        
        results['overall_quality'] = all(results.values())
        return results
    
    @staticmethod
    def check_content_originality(content: str, existing_content: List[str]) -> bool:
        """Check if content is sufficiently original."""
        for existing in existing_content:
            if is_similar_content(content, existing, threshold=0.8):
                return False
        return True
