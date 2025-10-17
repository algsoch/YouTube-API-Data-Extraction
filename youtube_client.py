"""
YouTube API Client Module
Handles authentication, quota management, and rate limiting for YouTube Data API v3.
"""

import os
import time
import logging
from typing import Optional
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuotaManager:
    """
    Manages YouTube API quota usage.
    
    YouTube Data API v3 has a default quota of 10,000 units per day.
    - Search costs 100 units per request
    - Videos.list costs 1 unit per request
    - Channels.list costs 1 unit per request
    """
    
    # Quota costs for different operations
    COSTS = {
        'search': 100,
        'videos': 1,
        'channels': 1
    }
    
    def __init__(self, daily_limit: int = 10000):
        self.daily_limit = daily_limit
        self.used_quota = 0
        self.request_count = 0
        
    def can_make_request(self, operation: str) -> bool:
        """Check if we have enough quota for an operation."""
        cost = self.COSTS.get(operation, 1)
        return (self.used_quota + cost) <= self.daily_limit
    
    def record_request(self, operation: str):
        """Record a request and update quota usage."""
        cost = self.COSTS.get(operation, 1)
        self.used_quota += cost
        self.request_count += 1
        logger.debug(f"Quota used: {self.used_quota}/{self.daily_limit} (Request: {operation}, Cost: {cost})")
    
    def get_remaining_quota(self) -> int:
        """Get remaining quota."""
        return self.daily_limit - self.used_quota
    
    def reset_quota(self):
        """Reset quota counter (call at midnight PST)."""
        self.used_quota = 0
        self.request_count = 0
        logger.info("Quota counter reset.")


class YouTubeAPIClient:
    """
    YouTube Data API v3 Client with quota management and rate limiting.
    """
    
    def __init__(self, api_key: Optional[str] = None, daily_quota: int = 10000):
        """
        Initialize YouTube API client.
        
        Args:
            api_key: YouTube Data API key (if None, reads from YOUTUBE_API_KEY env var)
            daily_quota: Daily quota limit (default: 10,000)
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key not provided. Set YOUTUBE_API_KEY environment variable.")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.quota_manager = QuotaManager(daily_limit=daily_quota)
        
        # Rate limiting: max 1 request per second to be safe
        self.min_request_interval = 1.0
        self.last_request_time = 0
        
        logger.info("YouTube API client initialized.")
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_videos(self, query: str, max_results: int = 50, 
                     page_token: Optional[str] = None, order: str = 'date') -> dict:
        """
        Search for videos using YouTube Data API.
        
        Args:
            query: Search query string
            max_results: Number of results per page (max 50)
            page_token: Token for pagination
            order: Sort order ('date', 'rating', 'relevance', 'title', 'viewCount')
        
        Returns:
            API response dict
        """
        if not self.quota_manager.can_make_request('search'):
            raise QuotaExceededError(f"Insufficient quota. Remaining: {self.quota_manager.get_remaining_quota()}")
        
        self._wait_for_rate_limit()
        
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=min(max_results, 50),
                pageToken=page_token,
                order=order
            )
            response = request.execute()
            
            self.quota_manager.record_request('search')
            logger.info(f"Search request completed: '{query}' (Results: {len(response.get('items', []))})")
            
            return response
            
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in str(e):
                logger.error("YouTube API quota exceeded!")
                raise QuotaExceededError("Daily quota limit exceeded. Quota resets at midnight Pacific Time.")
            logger.error(f"HTTP error during search: {e}")
            raise
    
    def get_video_details(self, video_ids: list) -> dict:
        """
        Get detailed information for a list of video IDs.
        
        Args:
            video_ids: List of video IDs (max 50 per request)
        
        Returns:
            API response dict
        """
        if not video_ids:
            return {'items': []}
        
        if not self.quota_manager.can_make_request('videos'):
            raise QuotaExceededError(f"Insufficient quota. Remaining: {self.quota_manager.get_remaining_quota()}")
        
        self._wait_for_rate_limit()
        
        # YouTube API allows up to 50 IDs per request
        video_ids = video_ids[:50]
        
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            )
            response = request.execute()
            
            self.quota_manager.record_request('videos')
            logger.debug(f"Video details fetched for {len(video_ids)} videos")
            
            return response
            
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in str(e):
                logger.error("YouTube API quota exceeded!")
                raise QuotaExceededError("Daily quota limit exceeded. Quota resets at midnight Pacific Time.")
            logger.error(f"HTTP error fetching video details: {e}")
            raise
    
    def get_channel_details(self, channel_ids: list) -> dict:
        """
        Get detailed information for a list of channel IDs.
        
        Args:
            channel_ids: List of channel IDs (max 50 per request)
        
        Returns:
            API response dict
        """
        if not channel_ids:
            return {'items': []}
        
        if not self.quota_manager.can_make_request('channels'):
            raise QuotaExceededError(f"Insufficient quota. Remaining: {self.quota_manager.get_remaining_quota()}")
        
        self._wait_for_rate_limit()
        
        # YouTube API allows up to 50 IDs per request
        channel_ids = channel_ids[:50]
        
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails,brandingSettings',
                id=','.join(channel_ids)
            )
            response = request.execute()
            
            self.quota_manager.record_request('channels')
            logger.debug(f"Channel details fetched for {len(channel_ids)} channels")
            
            return response
            
        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in str(e):
                logger.error("YouTube API quota exceeded!")
                raise QuotaExceededError("Daily quota limit exceeded. Quota resets at midnight Pacific Time.")
            logger.error(f"HTTP error fetching channel details: {e}")
            raise
    
    def get_quota_usage(self) -> dict:
        """Get current quota usage statistics."""
        return {
            'used': self.quota_manager.used_quota,
            'limit': self.quota_manager.daily_limit,
            'remaining': self.quota_manager.get_remaining_quota(),
            'requests': self.quota_manager.request_count
        }


class QuotaExceededError(Exception):
    """Raised when API quota is exceeded."""
    pass
