"""
Channel Data Extractor Module
Handles extracting channel profile data from YouTube.
"""

import logging
import time
from typing import List, Dict, Set
from youtube_client import YouTubeAPIClient, QuotaExceededError

logger = logging.getLogger(__name__)


class ChannelDataExtractor:
    """
    Extracts channel profile data from YouTube.
    """
    
    def __init__(self, api_client: YouTubeAPIClient):
        """
        Initialize channel data extractor.
        
        Args:
            api_client: YouTubeAPIClient instance
        """
        self.client = api_client
    
    def extract_unique_channel_ids(self, video_data: List[Dict[str, str]]) -> List[str]:
        """
        Extract unique channel IDs from video data.
        
        Args:
            video_data: List of video data dictionaries
        
        Returns:
            List of unique channel IDs
        """
        channel_ids = set()
        for video in video_data:
            channel_id = video.get('channelId', '').strip()
            if channel_id:
                channel_ids.add(channel_id)
        
        unique_ids = sorted(list(channel_ids))
        logger.info(f"Extracted {len(unique_ids)} unique channel IDs from {len(video_data)} videos")
        return unique_ids
    
    def extract_channel_data(self, channel_item: dict) -> Dict[str, str]:
        """
        Extract relevant fields from a channel API response.
        
        Args:
            channel_item: Channel item from API response
        
        Returns:
            Dictionary with channel data
        """
        snippet = channel_item.get('snippet', {})
        statistics = channel_item.get('statistics', {})
        branding = channel_item.get('brandingSettings', {}).get('channel', {})
        
        channel_id = channel_item.get('id', '')
        channel_url = f"https://www.youtube.com/channel/{channel_id}" if channel_id else ''
        
        return {
            'channelId': channel_id,
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'publishedAt': snippet.get('publishedAt', ''),
            'country': snippet.get('country', ''),
            'customUrl': snippet.get('customUrl', ''),
            'viewCount': statistics.get('viewCount', '0'),
            'subscriberCount': statistics.get('subscriberCount', '0'),
            'videoCount': statistics.get('videoCount', '0'),
            'hiddenSubscriberCount': str(statistics.get('hiddenSubscriberCount', False)),
            'channelUrl': channel_url
        }
    
    def get_channel_details(self, channel_ids: List[str]) -> List[Dict[str, str]]:
        """
        Fetch detailed information for a list of channel IDs.
        
        Args:
            channel_ids: List of channel IDs to fetch
        
        Returns:
            List of channel data dictionaries
        """
        if not channel_ids:
            return []
        
        channels = []
        batch_size = 50  # YouTube API allows up to 50 IDs per request
        total_batches = (len(channel_ids) + batch_size - 1) // batch_size
        
        logger.info(f"Fetching details for {len(channel_ids)} channels in {total_batches} batches")
        
        for i in range(0, len(channel_ids), batch_size):
            batch = channel_ids[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            # Check quota
            if not self.client.quota_manager.can_make_request('channels'):
                logger.warning(f"Quota limit reached. Collected {len(channels)} channel details so far.")
                break
            
            try:
                response = self.client.get_channel_details(batch)
                
                items = response.get('items', [])
                for item in items:
                    channel_data = self.extract_channel_data(item)
                    channels.append(channel_data)
                
                logger.info(f"Batch {batch_num}/{total_batches} complete: "
                          f"{len(items)} channels fetched ({len(channels)} total)")
                
                # Small delay between batches
                if i + batch_size < len(channel_ids):
                    time.sleep(0.5)
                    
            except QuotaExceededError as e:
                logger.warning(f"Quota exceeded: {e}. Stopping channel collection.")
                break
            except Exception as e:
                logger.error(f"Error fetching channel batch {batch_num}: {e}")
                # Continue with remaining batches
                continue
        
        logger.info(f"Channel data collection complete: {len(channels)} channels collected")
        return channels
    
    def get_channels_for_videos(self, video_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Extract unique channel IDs from videos and fetch their details.
        
        Args:
            video_data: List of video data dictionaries
        
        Returns:
            List of channel data dictionaries
        """
        channel_ids = self.extract_unique_channel_ids(video_data)
        
        if not channel_ids:
            logger.warning("No channel IDs found in video data")
            return []
        
        return self.get_channel_details(channel_ids)
    
    def get_channels_for_multiple_queries(self, 
                                         query_video_data: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
        """
        Extract unique channel IDs from multiple query results and fetch their details.
        
        Args:
            query_video_data: Dictionary mapping queries to their video data lists
        
        Returns:
            List of unique channel data dictionaries
        """
        # Collect all channel IDs across all queries
        all_channel_ids = set()
        total_videos = 0
        
        for query, videos in query_video_data.items():
            total_videos += len(videos)
            for video in videos:
                channel_id = video.get('channelId', '').strip()
                if channel_id:
                    all_channel_ids.add(channel_id)
        
        unique_channel_ids = sorted(list(all_channel_ids))
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Channel Collection Summary:")
        logger.info(f"  Total videos: {total_videos}")
        logger.info(f"  Unique channels: {len(unique_channel_ids)}")
        logger.info(f"{'='*60}\n")
        
        return self.get_channel_details(unique_channel_ids)
