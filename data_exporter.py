"""
Data Export Module
Handles exporting video and channel data to CSV files.
"""

import os
import logging
import pandas as pd
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class DataExporter:
    """
    Exports video and channel data to CSV files.
    """
    
    def __init__(self, output_dir: str = 'data'):
        """
        Initialize data exporter.
        
        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def export_videos_to_csv(self, video_data: List[Dict[str, str]], 
                            filename: str = None) -> str:
        """
        Export video data to CSV file.
        
        Args:
            video_data: List of video data dictionaries
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to exported CSV file
        """
        if not video_data:
            logger.warning("No video data to export")
            return None
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'videos_{timestamp}.csv'
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create DataFrame with specified column order
        columns = ['videoId', 'title', 'description', 'publishedAt', 'channelTitle', 'channelId']
        df = pd.DataFrame(video_data, columns=columns)
        
        # Export to CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        logger.info(f"Exported {len(video_data)} videos to: {filepath}")
        return filepath
    
    def export_channels_to_csv(self, channel_data: List[Dict[str, str]], 
                               filename: str = None) -> str:
        """
        Export channel data to CSV file.
        
        Args:
            channel_data: List of channel data dictionaries
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to exported CSV file
        """
        if not channel_data:
            logger.warning("No channel data to export")
            return None
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'channels_{timestamp}.csv'
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create DataFrame with specified column order
        columns = [
            'channelId', 'title', 'description', 'publishedAt', 'country', 
            'customUrl', 'viewCount', 'subscriberCount', 'videoCount', 
            'hiddenSubscriberCount', 'channelUrl'
        ]
        df = pd.DataFrame(channel_data, columns=columns)
        
        # Export to CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        logger.info(f"Exported {len(channel_data)} channels to: {filepath}")
        return filepath
    
    def export_query_videos_to_csv(self, query_video_data: Dict[str, List[Dict[str, str]]], 
                                   filename: str = None) -> str:
        """
        Export video data from multiple queries to a single CSV file.
        Adds a 'searchQuery' column to identify which query each video came from.
        
        Args:
            query_video_data: Dictionary mapping queries to their video data lists
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to exported CSV file
        """
        if not query_video_data:
            logger.warning("No query video data to export")
            return None
        
        # Combine all videos and add search query column
        all_videos = []
        for query, videos in query_video_data.items():
            for video in videos:
                video_with_query = video.copy()
                video_with_query['searchQuery'] = query
                all_videos.append(video_with_query)
        
        if not all_videos:
            logger.warning("No videos found in query data")
            return None
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'all_videos_{timestamp}.csv'
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create DataFrame with specified column order (searchQuery first)
        columns = ['searchQuery', 'videoId', 'title', 'description', 
                  'publishedAt', 'channelTitle', 'channelId']
        df = pd.DataFrame(all_videos, columns=columns)
        
        # Export to CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        logger.info(f"Exported {len(all_videos)} videos from {len(query_video_data)} queries to: {filepath}")
        return filepath
    
    def export_separate_query_csvs(self, query_video_data: Dict[str, List[Dict[str, str]]], 
                                   prefix: str = 'videos') -> List[str]:
        """
        Export each query's video data to separate CSV files.
        
        Args:
            query_video_data: Dictionary mapping queries to their video data lists
            prefix: Prefix for output filenames
        
        Returns:
            List of paths to exported CSV files
        """
        exported_files = []
        
        for query, videos in query_video_data.items():
            # Create safe filename from query
            safe_query = query.replace(' ', '_').replace('/', '_')
            safe_query = ''.join(c for c in safe_query if c.isalnum() or c in ('_', '-'))
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{prefix}_{safe_query}_{timestamp}.csv"
            
            filepath = self.export_videos_to_csv(videos, filename)
            if filepath:
                exported_files.append(filepath)
        
        logger.info(f"Exported {len(exported_files)} separate CSV files")
        return exported_files
    
    def export_summary_report(self, query_video_data: Dict[str, List[Dict[str, str]]], 
                             channel_data: List[Dict[str, str]], 
                             quota_usage: dict) -> str:
        """
        Export a summary report of the data collection.
        
        Args:
            query_video_data: Dictionary mapping queries to their video data lists
            channel_data: List of channel data dictionaries
            quota_usage: Quota usage statistics
        
        Returns:
            Path to summary report file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'extraction_summary_{timestamp}.txt'
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("YouTube Data Extraction Summary\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Video Collection Summary:\n")
            f.write("-" * 70 + "\n")
            total_videos = 0
            for query, videos in query_video_data.items():
                f.write(f"  {query}: {len(videos)} videos\n")
                total_videos += len(videos)
            f.write(f"\n  TOTAL VIDEOS: {total_videos}\n\n")
            
            f.write("Channel Collection Summary:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Unique Channels: {len(channel_data)}\n\n")
            
            f.write("API Quota Usage:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Used: {quota_usage.get('used', 0)}\n")
            f.write(f"  Limit: {quota_usage.get('limit', 0)}\n")
            f.write(f"  Remaining: {quota_usage.get('remaining', 0)}\n")
            f.write(f"  Total Requests: {quota_usage.get('requests', 0)}\n\n")
            
            f.write("="*70 + "\n")
        
        logger.info(f"Exported summary report to: {filepath}")
        return filepath
