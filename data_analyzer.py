"""
Data Analysis Module
Provides comprehensive analytics for YouTube video and channel data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
import logging

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """
    Analyzes YouTube video and channel data to provide insights and statistics.
    """
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize data analyzer.
        
        Args:
            data_dir: Directory containing CSV data files
        """
        self.data_dir = data_dir
        self.videos_df = None
        self.channels_df = None
    
    def load_latest_data(self) -> bool:
        """Load the most recent CSV files from data directory."""
        try:
            # Find latest video CSV
            video_files = [f for f in os.listdir(self.data_dir) if f.startswith('classical_music_videos_') and f.endswith('.csv')]
            if video_files:
                latest_video = max(video_files)
                self.videos_df = pd.read_csv(os.path.join(self.data_dir, latest_video))
                logger.info(f"Loaded video data: {latest_video} ({len(self.videos_df)} records)")
            
            # Find latest channel CSV
            channel_files = [f for f in os.listdir(self.data_dir) if f.startswith('classical_music_channels_') and f.endswith('.csv')]
            if channel_files:
                latest_channel = max(channel_files)
                self.channels_df = pd.read_csv(os.path.join(self.data_dir, latest_channel))
                logger.info(f"Loaded channel data: {latest_channel} ({len(self.channels_df)} records)")
            
            return self.videos_df is not None or self.channels_df is not None
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def get_overview_statistics(self) -> Dict[str, Any]:
        """Get high-level overview statistics."""
        if self.videos_df is None:
            return {"error": "No data loaded"}
        
        stats = {
            "total_videos": len(self.videos_df),
            "total_channels": self.channels_df is not None and len(self.channels_df) or self.videos_df['channelId'].nunique(),
            "search_queries": self.videos_df['searchQuery'].nunique() if 'searchQuery' in self.videos_df.columns else 0,
            "date_range": {
                "earliest": self.videos_df['publishedAt'].min() if 'publishedAt' in self.videos_df.columns else None,
                "latest": self.videos_df['publishedAt'].max() if 'publishedAt' in self.videos_df.columns else None
            }
        }
        
        if self.channels_df is not None:
            stats["total_views"] = self.channels_df['viewCount'].astype(float).sum()
            stats["total_subscribers"] = self.channels_df['subscriberCount'].astype(float).sum()
            stats["avg_subscribers_per_channel"] = self.channels_df['subscriberCount'].astype(float).mean()
        
        return stats
    
    def get_query_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics per search query."""
        if self.videos_df is None or 'searchQuery' not in self.videos_df.columns:
            return []
        
        query_stats = []
        for query in self.videos_df['searchQuery'].unique():
            query_videos = self.videos_df[self.videos_df['searchQuery'] == query]
            
            stats = {
                "query": query,
                "video_count": len(query_videos),
                "unique_channels": query_videos['channelId'].nunique(),
                "avg_videos_per_channel": len(query_videos) / query_videos['channelId'].nunique()
            }
            query_stats.append(stats)
        
        return sorted(query_stats, key=lambda x: x['video_count'], reverse=True)
    
    def get_top_channels(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top channels by various metrics."""
        if self.channels_df is None:
            return []
        
        df = self.channels_df.copy()
        
        # Convert numeric columns
        df['viewCount'] = pd.to_numeric(df['viewCount'], errors='coerce').fillna(0)
        df['subscriberCount'] = pd.to_numeric(df['subscriberCount'], errors='coerce').fillna(0)
        df['videoCount'] = pd.to_numeric(df['videoCount'], errors='coerce').fillna(0)
        
        top_channels = df.nlargest(limit, 'subscriberCount')[
            ['channelId', 'title', 'subscriberCount', 'viewCount', 'videoCount', 'country']
        ].to_dict('records')
        
        return top_channels
    
    def get_temporal_distribution(self) -> Dict[str, Any]:
        """Get temporal distribution of videos."""
        if self.videos_df is None or 'publishedAt' not in self.videos_df.columns:
            return {}
        
        df = self.videos_df.copy()
        df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')
        df['year'] = df['publishedAt'].dt.year
        df['month'] = df['publishedAt'].dt.to_period('M').astype(str)
        
        return {
            "by_year": df['year'].value_counts().sort_index().to_dict(),
            "by_month": df['month'].value_counts().sort_index().tail(24).to_dict(),
            "recent_uploads": df[df['publishedAt'] > (datetime.now() - timedelta(days=30))].groupby('searchQuery').size().to_dict()
        }
    
    def get_channel_distribution(self) -> Dict[str, Any]:
        """Get channel distribution statistics."""
        if self.videos_df is None:
            return {}
        
        # Videos per channel
        videos_per_channel = self.videos_df.groupby('channelId').size()
        
        distribution = {
            "videos_per_channel": {
                "mean": float(videos_per_channel.mean()),
                "median": float(videos_per_channel.median()),
                "max": int(videos_per_channel.max()),
                "min": int(videos_per_channel.min())
            },
            "top_contributors": self.videos_df.groupby('channelTitle').size().nlargest(10).to_dict()
        }
        
        if self.channels_df is not None:
            # Country distribution
            country_dist = self.channels_df['country'].value_counts().head(10).to_dict()
            distribution["by_country"] = country_dist
        
        return distribution
    
    def search_videos(self, query: str = "", channel: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """Search videos with filters."""
        if self.videos_df is None:
            return []
        
        df = self.videos_df.copy()
        
        if query:
            mask = df['title'].str.contains(query, case=False, na=False) | \
                   df['description'].str.contains(query, case=False, na=False)
            df = df[mask]
        
        if channel:
            df = df[df['channelTitle'].str.contains(channel, case=False, na=False)]
        
        return df.head(limit).to_dict('records')
    
    def get_engagement_metrics(self) -> Dict[str, Any]:
        """Calculate engagement metrics from channel data."""
        if self.channels_df is None:
            return {}
        
        df = self.channels_df.copy()
        df['viewCount'] = pd.to_numeric(df['viewCount'], errors='coerce').fillna(0)
        df['subscriberCount'] = pd.to_numeric(df['subscriberCount'], errors='coerce').fillna(0)
        df['videoCount'] = pd.to_numeric(df['videoCount'], errors='coerce').fillna(0)
        
        # Calculate engagement ratios
        df['views_per_video'] = df['viewCount'] / df['videoCount'].replace(0, 1)
        df['views_per_subscriber'] = df['viewCount'] / df['subscriberCount'].replace(0, 1)
        
        return {
            "avg_views_per_video": float(df['views_per_video'].mean()),
            "avg_views_per_subscriber": float(df['views_per_subscriber'].mean()),
            "total_reach": {
                "views": int(df['viewCount'].sum()),
                "subscribers": int(df['subscriberCount'].sum()),
                "videos": int(df['videoCount'].sum())
            },
            "top_engagement_channels": df.nlargest(10, 'views_per_video')[
                ['title', 'views_per_video', 'subscriberCount']
            ].to_dict('records')
        }
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report."""
        return {
            "overview": self.get_overview_statistics(),
            "query_stats": self.get_query_statistics(),
            "top_channels": self.get_top_channels(10),
            "temporal": self.get_temporal_distribution(),
            "distribution": self.get_channel_distribution(),
            "engagement": self.get_engagement_metrics(),
            "generated_at": datetime.now().isoformat()
        }
    
    def export_analysis_report(self, filename: str = None) -> str:
        """Export analysis report to JSON."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'analysis_report_{timestamp}.json'
        
        filepath = os.path.join(self.data_dir, filename)
        
        report = self.generate_summary_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Analysis report exported to: {filepath}")
        return filepath
    
    def get_top_videos_by_engagement(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get top videos based on engagement metrics (if available)."""
        if self.videos_df is None:
            return []
        
        df = self.videos_df.copy()
        
        # Select relevant columns
        columns = ['videoId', 'title', 'channelTitle', 'publishedAt', 'searchQuery']
        if 'viewCount' in df.columns:
            columns.append('viewCount')
            df['viewCount'] = pd.to_numeric(df['viewCount'], errors='coerce').fillna(0)
        
        result_df = df[columns].head(limit)
        return result_df.to_dict('records')
    
    def get_channel_rankings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get comprehensive channel rankings by multiple metrics."""
        if self.channels_df is None:
            return {}
        
        df = self.channels_df.copy()
        
        # Convert numeric columns and handle NaN
        for col in ['viewCount', 'subscriberCount', 'videoCount']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Fill NaN values in string columns with empty strings
        df = df.fillna('')
        
        rankings = {}
        
        # Top by subscribers
        if 'subscriberCount' in df.columns:
            rankings['most_subscribed'] = df.nlargest(20, 'subscriberCount')[
                ['channelId', 'title', 'subscriberCount', 'viewCount', 'videoCount', 'country', 'channelUrl']
            ].replace({np.nan: '', np.inf: 0, -np.inf: 0}).to_dict('records')
            
            rankings['least_subscribed'] = df[df['subscriberCount'] > 0].nsmallest(20, 'subscriberCount')[
                ['channelId', 'title', 'subscriberCount', 'viewCount', 'videoCount', 'country', 'channelUrl']
            ].replace({np.nan: '', np.inf: 0, -np.inf: 0}).to_dict('records')
        
        # Top by views
        if 'viewCount' in df.columns:
            rankings['most_viewed'] = df.nlargest(20, 'viewCount')[
                ['channelId', 'title', 'subscriberCount', 'viewCount', 'videoCount', 'country', 'channelUrl']
            ].replace({np.nan: '', np.inf: 0, -np.inf: 0}).to_dict('records')
            
            rankings['least_viewed'] = df[df['viewCount'] > 0].nsmallest(20, 'viewCount')[
                ['channelId', 'title', 'subscriberCount', 'viewCount', 'videoCount', 'country', 'channelUrl']
            ].replace({np.nan: '', np.inf: 0, -np.inf: 0}).to_dict('records')
        
        # Most prolific (most videos)
        if 'videoCount' in df.columns:
            rankings['most_videos'] = df.nlargest(20, 'videoCount')[
                ['channelId', 'title', 'subscriberCount', 'viewCount', 'videoCount', 'country', 'channelUrl']
            ].replace({np.nan: '', np.inf: 0, -np.inf: 0}).to_dict('records')
        
        # By country distribution
        if 'country' in df.columns:
            country_stats = df.groupby('country').agg({
                'channelId': 'count',
                'subscriberCount': 'sum',
                'viewCount': 'sum'
            }).reset_index()
            country_stats.columns = ['country', 'channel_count', 'total_subscribers', 'total_views']
            # Replace NaN and Inf values before converting to dict
            country_stats = country_stats.replace({np.nan: 0, np.inf: 0, -np.inf: 0})
            rankings['by_country'] = country_stats.sort_values('channel_count', ascending=False).head(20).to_dict('records')
        
        return rankings
    
    def get_video_statistics(self) -> Dict[str, Any]:
        """Get detailed video statistics."""
        if self.videos_df is None:
            return {}
        
        df = self.videos_df.copy()
        
        stats = {
            'total_videos': int(len(df)),
            'unique_channels': int(df['channelId'].nunique()) if 'channelId' in df.columns else 0,
            'unique_queries': int(df['searchQuery'].nunique()) if 'searchQuery' in df.columns else 0
        }
        
        # Date analysis
        if 'publishedAt' in df.columns:
            df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')
            earliest = df['publishedAt'].min()
            latest = df['publishedAt'].max()
            
            stats['date_range'] = {
                'earliest': earliest.isoformat() if pd.notna(earliest) else None,
                'latest': latest.isoformat() if pd.notna(latest) else None,
                'span_days': int((latest - earliest).days) if pd.notna(earliest) and pd.notna(latest) else 0
            }
            
            # Videos by year - handle NaN and convert to int
            df['year'] = df['publishedAt'].dt.year
            year_counts = df['year'].value_counts().sort_index()
            stats['videos_by_year'] = {
                int(year): int(count) for year, count in year_counts.items() if pd.notna(year)
            }
        
        # Query distribution
        if 'searchQuery' in df.columns:
            query_dist = df['searchQuery'].value_counts().head(20)
            stats['top_queries'] = [
                {'query': str(query), 'count': int(count)} 
                for query, count in query_dist.items() if pd.notna(query)
            ]
        
        # Channel distribution
        if 'channelTitle' in df.columns:
            channel_dist = df['channelTitle'].value_counts().head(20)
            stats['top_channels_by_video_count'] = [
                {'channel': str(channel), 'video_count': int(count)}
                for channel, count in channel_dist.items() if pd.notna(channel)
            ]
        
        return stats
