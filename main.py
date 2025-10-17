"""
Main Script for YouTube Classical Music Data Extraction
Orchestrates the collection of video and channel data for classical music search phrases.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict

from youtube_client import YouTubeAPIClient
from video_extractor import VideoDataExtractor
from channel_extractor import ChannelDataExtractor
from data_exporter import DataExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Classical music search phrases
SEARCH_PHRASES = [
    "Beethoven Symphony",
    "Handel Messiah",
    "Mozart Requiem",
    "Mozart Coronation Mass",
    "Bach St Matthew Passion",
    "Bach St John Passion",
    "Brahms A German Requiem",
    "Haydn The Creation",
    "Haydn The Seasons",
    "Faure Requiem",
    "Faure Cantique de Jean Racine",
    "Vivaldi Gloria",
    "Bach Magnificat",
    "Mendelssohn Elijah",
    "Schubert Mass",
    "Beethoven Missa Solemnis",
    "Mozart Ave Verum"
]

# Configuration
VIDEOS_PER_QUERY = 2000
PROGRESS_FILE = 'extraction_progress.json'


class ProgressTracker:
    """Tracks extraction progress and allows resuming from checkpoint."""
    
    def __init__(self, progress_file: str = PROGRESS_FILE):
        self.progress_file = progress_file
        self.progress = self._load_progress()
    
    def _load_progress(self) -> dict:
        """Load progress from file."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
        
        return {
            'completed_queries': [],
            'video_data': {},
            'last_updated': None
        }
    
    def save_progress(self, completed_queries: List[str], video_data: Dict[str, List[Dict]]):
        """Save current progress to file."""
        self.progress = {
            'completed_queries': completed_queries,
            'video_data': video_data,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
            logger.info(f"Progress saved to {self.progress_file}")
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def get_remaining_queries(self, all_queries: List[str]) -> List[str]:
        """Get list of queries that haven't been completed yet."""
        completed = set(self.progress.get('completed_queries', []))
        return [q for q in all_queries if q not in completed]
    
    def get_completed_data(self) -> Dict[str, List[Dict]]:
        """Get video data from completed queries."""
        return self.progress.get('video_data', {})


def main():
    """Main execution function."""
    
    logger.info("="*70)
    logger.info("YouTube Classical Music Data Extraction")
    logger.info("="*70)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize components
    try:
        api_client = YouTubeAPIClient()
        video_extractor = VideoDataExtractor(api_client)
        channel_extractor = ChannelDataExtractor(api_client)
        data_exporter = DataExporter(output_dir='data')
        progress_tracker = ProgressTracker()
    except ValueError as e:
        logger.error(f"Initialization failed: {e}")
        logger.error("Please ensure YOUTUBE_API_KEY is set in .env file")
        return
    
    # Check for existing progress
    completed_data = progress_tracker.get_completed_data()
    remaining_queries = progress_tracker.get_remaining_queries(SEARCH_PHRASES)
    
    if completed_data:
        logger.info(f"\nResuming from previous session:")
        logger.info(f"  Already completed: {len(completed_data)} queries")
        logger.info(f"  Remaining: {len(remaining_queries)} queries\n")
    else:
        logger.info(f"Starting fresh extraction for {len(SEARCH_PHRASES)} search phrases\n")
    
    # Extract video data for remaining queries
    logger.info("="*70)
    logger.info("PHASE 1: VIDEO DATA COLLECTION")
    logger.info("="*70)
    
    all_video_data = completed_data.copy()
    
    if remaining_queries:
        logger.info(f"Collecting {VIDEOS_PER_QUERY} most recent videos per phrase...")
        
        try:
            # Process queries one at a time for better progress tracking
            for i, query in enumerate(remaining_queries, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing query {i}/{len(remaining_queries)}: '{query}'")
                logger.info(f"{'='*60}")
                
                # Check quota before starting
                quota_info = api_client.get_quota_usage()
                logger.info(f"Current quota: {quota_info['used']}/{quota_info['limit']} "
                          f"({quota_info['remaining']} remaining)")
                
                # Estimate if we have enough quota (rough: 2000 videos needs ~40 search requests = 4000 quota)
                if quota_info['remaining'] < 4000:
                    logger.warning(f"\nInsufficient quota to continue. Saving progress...")
                    logger.warning(f"Please wait for quota reset (midnight Pacific Time) and run again.")
                    break
                
                # Search for videos
                videos = video_extractor.search_videos(query, max_videos=VIDEOS_PER_QUERY, order='date')
                all_video_data[query] = videos
                
                # Save progress after each query
                completed_queries = list(all_video_data.keys())
                progress_tracker.save_progress(completed_queries, all_video_data)
                
                logger.info(f"✓ Completed '{query}': {len(videos)} videos collected")
                
        except KeyboardInterrupt:
            logger.info("\n\nExtraction interrupted by user. Saving progress...")
            completed_queries = list(all_video_data.keys())
            progress_tracker.save_progress(completed_queries, all_video_data)
            logger.info("Progress saved. Run the script again to resume.")
            return
        except Exception as e:
            logger.error(f"\n\nError during extraction: {e}")
            logger.info("Saving progress before exit...")
            completed_queries = list(all_video_data.keys())
            progress_tracker.save_progress(completed_queries, all_video_data)
            raise
    else:
        logger.info("All video data already collected from previous session.")
    
    # Summary of video collection
    total_videos = sum(len(videos) for videos in all_video_data.values())
    logger.info(f"\n{'='*70}")
    logger.info(f"VIDEO COLLECTION COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Total Queries: {len(all_video_data)}")
    logger.info(f"Total Videos: {total_videos}")
    logger.info(f"{'='*70}\n")
    
    # Extract channel data
    logger.info("="*70)
    logger.info("PHASE 2: CHANNEL DATA COLLECTION")
    logger.info("="*70)
    
    try:
        channel_data = channel_extractor.get_channels_for_multiple_queries(all_video_data)
        logger.info(f"✓ Collected data for {len(channel_data)} unique channels\n")
    except Exception as e:
        logger.error(f"Error collecting channel data: {e}")
        channel_data = []
    
    # Export data to CSV
    logger.info("="*70)
    logger.info("PHASE 3: DATA EXPORT")
    logger.info("="*70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Export all videos to a single CSV
    videos_file = data_exporter.export_query_videos_to_csv(
        all_video_data, 
        filename=f'classical_music_videos_{timestamp}.csv'
    )
    
    # Export channels to CSV
    channels_file = data_exporter.export_channels_to_csv(
        channel_data,
        filename=f'classical_music_channels_{timestamp}.csv'
    )
    
    # Export summary report
    quota_usage = api_client.get_quota_usage()
    summary_file = data_exporter.export_summary_report(
        all_video_data,
        channel_data,
        quota_usage
    )
    
    # Final summary
    logger.info("\n" + "="*70)
    logger.info("EXTRACTION COMPLETE!")
    logger.info("="*70)
    logger.info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"\nDeliverables:")
    logger.info(f"  Videos CSV: {videos_file}")
    logger.info(f"  Channels CSV: {channels_file}")
    logger.info(f"  Summary Report: {summary_file}")
    logger.info(f"\nStatistics:")
    logger.info(f"  Total Videos: {total_videos}")
    logger.info(f"  Total Channels: {len(channel_data)}")
    logger.info(f"  Quota Used: {quota_usage['used']}/{quota_usage['limit']}")
    logger.info("="*70)
    
    # Clean up progress file on successful completion
    if len(all_video_data) == len(SEARCH_PHRASES):
        try:
            if os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
                logger.info(f"\nProgress file removed (extraction complete)")
        except Exception as e:
            logger.warning(f"Could not remove progress file: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"\nFatal error: {e}", exc_info=True)
        logger.error("\nExtraction failed. Check the log file for details.")
