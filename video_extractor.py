"""
Video Data Extractor Module
Handles searching and extracting video data from YouTube.
"""

import logging
import time
from typing import List, Dict, Optional
from youtube_client import YouTubeAPIClient, QuotaExceededError

logger = logging.getLogger(__name__)


class VideoDataExtractor:
    """
    Extracts video data from YouTube for specific search queries.
    """
    
    def __init__(self, api_client: YouTubeAPIClient):
        """
        Initialize video data extractor.
        
        Args:
            api_client: YouTubeAPIClient instance
        """
        self.client = api_client
    
    def extract_video_data(self, video_item: dict) -> Dict[str, str]:
        """
        Extract relevant fields from a video search result.
        
        Args:
            video_item: Video item from API response
        
        Returns:
            Dictionary with video data
        """
        snippet = video_item.get('snippet', {})
        video_id = video_item.get('id', {})
        
        # Handle different response formats
        if isinstance(video_id, dict):
            video_id = video_id.get('videoId', '')
        
        return {
            'videoId': video_id,
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'publishedAt': snippet.get('publishedAt', ''),
            'channelTitle': snippet.get('channelTitle', ''),
            'channelId': snippet.get('channelId', '')
        }
    
    def search_videos(self, query: str, max_videos: int = 2000, 
                     order: str = 'date') -> List[Dict[str, str]]:
        """
        Search for videos and extract data.
        
        Args:
            query: Search query string
            max_videos: Maximum number of videos to retrieve
            order: Sort order ('date' for most recent)
        
        Returns:
            List of video data dictionaries
        """
        videos = []
        page_token = None
        videos_per_page = 50  # Maximum allowed by YouTube API
        
        logger.info(f"Starting video search: '{query}' (Target: {max_videos} videos)")
        
        try:
            while len(videos) < max_videos:
                # Calculate how many results to request
                remaining = max_videos - len(videos)
                results_to_request = min(videos_per_page, remaining)
                
                # Check quota before making request
                if not self.client.quota_manager.can_make_request('search'):
                    logger.warning(f"Quota limit reached. Collected {len(videos)} videos so far.")
                    break
                
                # Make search request
                try:
                    response = self.client.search_videos(
                        query=query,
                        max_results=results_to_request,
                        page_token=page_token,
                        order=order
                    )
                except QuotaExceededError as e:
                    logger.warning(f"Quota exceeded: {e}. Stopping collection.")
                    break
                
                # Extract video data from response
                items = response.get('items', [])
                if not items:
                    logger.info(f"No more results found. Total videos collected: {len(videos)}")
                    break
                
                for item in items:
                    video_data = self.extract_video_data(item)
                    if video_data['videoId']:  # Only add if we have a valid video ID
                        videos.append(video_data)
                
                logger.info(f"Progress: {len(videos)}/{max_videos} videos collected for '{query}'")
                
                # Check for next page
                page_token = response.get('nextPageToken')
                if not page_token:
                    logger.info(f"Reached end of results. Total videos collected: {len(videos)}")
                    break
                
                # Small delay between requests (in addition to rate limiting in client)
                time.sleep(0.5)
            
            logger.info(f"Completed search for '{query}': {len(videos)} videos collected")
            return videos[:max_videos]  # Ensure we don't exceed max_videos
            
        except Exception as e:
            logger.error(f"Error during video search for '{query}': {e}")
            logger.info(f"Returning {len(videos)} videos collected before error")
            return videos
    
    def search_multiple_queries(self, queries: List[str], 
                               videos_per_query: int = 2000) -> Dict[str, List[Dict[str, str]]]:
        """
        Search for videos across multiple queries.
        
        Args:
            queries: List of search query strings
            videos_per_query: Number of videos to retrieve per query
        
        Returns:
            Dictionary mapping query to list of video data
        """
        results = {}
        
        for i, query in enumerate(queries, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing query {i}/{len(queries)}: '{query}'")
            logger.info(f"{'='*60}")
            
            quota_info = self.client.get_quota_usage()
            logger.info(f"Quota status: {quota_info['used']}/{quota_info['limit']} "
                       f"({quota_info['remaining']} remaining)")
            
            # Check if we have enough quota (rough estimate: 2000 videos needs ~40 search requests)
            estimated_cost = (videos_per_query // 50 + 1) * 100
            if quota_info['remaining'] < estimated_cost:
                logger.warning(f"Insufficient quota for full search. "
                             f"Estimated cost: {estimated_cost}, Available: {quota_info['remaining']}")
                logger.info(f"Stopping at query {i-1}/{len(queries)}. Resume later to continue.")
                break
            
            videos = self.search_videos(query, max_videos=videos_per_query, order='date')
            results[query] = videos
            
            logger.info(f"Query '{query}' complete: {len(videos)} videos collected")
            
            # Add a small delay between different queries
            if i < len(queries):
                logger.info("Pausing 2 seconds before next query...")
                time.sleep(2)
        
        return results
