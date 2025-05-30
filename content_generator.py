"""
Content generation using Gemini AI for blockchain projects.
Creates analytical and insightful content about crypto/blockchain projects.
"""

import google.generativeai as genai
import logging
import re
import random
from typing import Optional, Dict, List
from datetime import datetime

class ContentGenerator:
    """Generates analytical content using Gemini AI."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_gemini()
        
    def _initialize_gemini(self):
        """Initialize Gemini AI with API key."""
        import os
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
            
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.logger.info("Gemini AI initialized successfully")
        
    def generate_content(self, project_name: str, website: str, twitter_handle: str, 
                        recent_content: List[str] = None) -> Optional[str]:
        """Generate analytical content for a blockchain project."""
        try:
            # Create the prompt for content generation
            prompt = self._create_content_prompt(project_name, website, twitter_handle, recent_content)
            
            # Generate content using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 300,
                }
            )
            
            if response and response.text:
                content = self._clean_and_validate_content(response.text)
                if content:
                    self.logger.info(f"Generated content for {project_name}: {len(content)} characters")
                    return content
                else:
                    self.logger.warning(f"Generated content for {project_name} failed validation")
                    return None
            else:
                self.logger.error(f"No content generated for {project_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating content for {project_name}: {str(e)}")
            return None
            
    def _create_content_prompt(self, project_name: str, website: str, twitter_handle: str, 
                              recent_content: List[str] = None) -> str:
        """Create a detailed prompt for content generation."""
        
        # Content style variations
        content_types = [
            "analytical deep dive",
            "market perspective",
            "technical analysis",
            "ecosystem comparison",
            "future potential assessment",
            "innovation spotlight",
            "competitive analysis"
        ]
        
        selected_type = random.choice(content_types)
        
        prompt = f"""
        Write a {selected_type} Twitter thread about {project_name} ({website}, {twitter_handle}).

        CRITICAL REQUIREMENTS:
        1. Must be analytical and insightful, not just descriptive
        2. Include your own interpretation and perspective
        3. Explain WHY this project matters, not just WHAT it does
        4. Discuss potential, advantages, and challenges
        5. Use comparative examples when relevant
        6. Create unique value beyond basic Google search results
        7. Maximum 280 characters per tweet (Twitter limit)
        8. Write 2-4 connected tweets that form a cohesive thread
        9. Include relevant hashtags and mention {twitter_handle}

        CONTENT STYLE:
        - Be thought-provoking and engaging
        - Use data points or metrics when possible
        - Maintain professional yet conversational tone
        - Avoid generic buzzwords
        - Focus on unique insights and implications

        AVOID:
        - Basic project descriptions
        - Generic marketing language
        - Copy-paste information from websites
        - Surface-level observations
        """
        
        # Add context about recent content to avoid repetition
        if recent_content:
            prompt += f"\n\nAVOID REPEATING these recent topics:\n"
            for content in recent_content[:3]:  # Last 3 posts
                prompt += f"- {content[:100]}...\n"
                
        prompt += f"\n\nGenerate the Twitter thread now:"
        
        return prompt
        
    def _clean_and_validate_content(self, content: str) -> Optional[str]:
        """Clean and validate the generated content."""
        if not content:
            return None
            
        # Remove extra whitespace and clean formatting
        content = re.sub(r'\n\s*\n', '\n\n', content.strip())
        
        # Split into individual tweets if it's a thread
        tweets = self._split_into_tweets(content)
        
        if not tweets:
            return None
            
        # Validate each tweet
        validated_tweets = []
        for tweet in tweets:
            tweet = tweet.strip()
            
            # Check length (Twitter limit is 280 characters)
            if len(tweet) > 280:
                # Try to truncate intelligently
                tweet = self._truncate_tweet(tweet)
                
            if len(tweet) < 50:  # Too short, not valuable
                continue
                
            validated_tweets.append(tweet)
            
        if not validated_tweets:
            return None
            
        # Join tweets for thread format
        if len(validated_tweets) == 1:
            return validated_tweets[0]
        else:
            # Number the tweets for thread format
            numbered_tweets = []
            for i, tweet in enumerate(validated_tweets, 1):
                if i == 1:
                    numbered_tweets.append(f"{tweet} 🧵")
                else:
                    numbered_tweets.append(f"{i}/{len(validated_tweets)} {tweet}")
            return "\n\n".join(numbered_tweets)
            
    def _split_into_tweets(self, content: str) -> List[str]:
        """Split content into individual tweets."""
        # Look for natural break points
        paragraphs = content.split('\n\n')
        tweets = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If paragraph is short enough, it's one tweet
            if len(paragraph) <= 280:
                tweets.append(paragraph)
            else:
                # Split long paragraphs at sentence boundaries
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                current_tweet = ""
                
                for sentence in sentences:
                    if len(current_tweet + " " + sentence) <= 280:
                        current_tweet += (" " + sentence) if current_tweet else sentence
                    else:
                        if current_tweet:
                            tweets.append(current_tweet)
                        current_tweet = sentence
                        
                if current_tweet:
                    tweets.append(current_tweet)
                    
        return tweets
        
    def _truncate_tweet(self, tweet: str) -> str:
        """Intelligently truncate a tweet to fit Twitter's character limit."""
        if len(tweet) <= 280:
            return tweet
            
        # Try to cut at sentence boundary
        sentences = re.split(r'(?<=[.!?])\s+', tweet)
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + " " + sentence) <= 277:  # Leave room for "..."
                truncated += (" " + sentence) if truncated else sentence
            else:
                break
                
        if truncated:
            return truncated + "..."
        else:
            # Cut at word boundary
            words = tweet.split()
            truncated = ""
            
            for word in words:
                if len(truncated + " " + word) <= 277:
                    truncated += (" " + word) if truncated else word
                else:
                    break
                    
            return truncated + "..." if truncated else tweet[:277] + "..."
            
    def generate_project_analysis(self, project_name: str, project_data: Dict) -> str:
        """Generate a comprehensive analysis prompt for a specific project."""
        return f"""
        Analyze {project_name} from multiple angles:
        
        1. TECHNOLOGY INNOVATION: What technical innovations does {project_name} bring?
        2. MARKET POSITION: How does it compare to competitors?
        3. ADOPTION POTENTIAL: What drives user/developer adoption?
        4. RISKS & CHALLENGES: What obstacles might it face?
        5. LONG-TERM VISION: Where could this project be in 2-3 years?
        
        Create insights that go beyond surface-level descriptions.
        Focus on implications and strategic significance.
        """
