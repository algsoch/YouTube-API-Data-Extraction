"""
FastAPI Application for YouTube Classical Music Data Extraction
Provides REST API endpoints and web interface for data collection and analysis.
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import json
import logging
from datetime import datetime, timezone, timedelta
import asyncio
import pytz

from youtube_client import YouTubeAPIClient, QuotaExceededError
from video_extractor import VideoDataExtractor
from channel_extractor import ChannelDataExtractor
from data_exporter import DataExporter
from data_analyzer import DataAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define base directory (absolute path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Classical Music Data Extraction API",
    description="Extract and analyze YouTube video and channel data for classical music",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global state
extraction_status = {
    "is_running": False,
    "current_query": None,
    "progress": 0,
    "total_queries": 0,
    "completed_queries": [],
    "videos_collected": 0,
    "channels_collected": 0,
    "quota_used": 0,
    "quota_limit": 10000,
    "quota_exceeded": False,
    "errors": [],
    "started_at": None,
    "last_updated": None
}

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


# Pydantic models
class ExtractionConfig(BaseModel):
    queries: Optional[List[str]] = None
    videos_per_query: int = 2000
    daily_quota: int = 10000


class AnalysisRequest(BaseModel):
    query: Optional[str] = None
    channel: Optional[str] = None
    limit: int = 100


class CustomQueryRequest(BaseModel):
    query: str
    max_videos: int = 100


# Helper functions
def get_quota_reset_time():
    """Calculate when YouTube API quota resets (midnight Pacific Time)."""
    pacific = pytz.timezone('America/Los_Angeles')
    now = datetime.now(pacific)
    
    # Next midnight Pacific Time
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Time until reset
    time_until_reset = next_midnight - now
    hours = int(time_until_reset.total_seconds() // 3600)
    minutes = int((time_until_reset.total_seconds() % 3600) // 60)
    
    return {
        "reset_time": next_midnight.isoformat(),
        "hours_until_reset": hours,
        "minutes_until_reset": minutes,
        "formatted": f"{hours}h {minutes}m"
    }


def load_progress():
    """Load extraction progress from file."""
    progress_file = "extraction_progress.json"
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
    return {"completed_queries": [], "video_data": {}}


def update_status(update_dict: Dict):
    """Update global extraction status."""
    global extraction_status
    extraction_status.update(update_dict)
    extraction_status["last_updated"] = datetime.now().isoformat()


async def run_extraction_task(config: ExtractionConfig):
    """Background task to run data extraction."""
    try:
        update_status({
            "is_running": True,
            "started_at": datetime.now().isoformat(),
            "total_queries": len(config.queries or SEARCH_PHRASES),
            "errors": []
        })
        
        # Initialize components
        api_client = YouTubeAPIClient(daily_quota=config.daily_quota)
        video_extractor = VideoDataExtractor(api_client)
        channel_extractor = ChannelDataExtractor(api_client)
        data_exporter = DataExporter(output_dir='data')
        
        # Load progress
        progress = load_progress()
        completed = set(progress.get('completed_queries', []))
        all_video_data = progress.get('video_data', {})
        
        queries = config.queries or SEARCH_PHRASES
        remaining_queries = [q for q in queries if q not in completed]
        
        # Extract videos
        for i, query in enumerate(remaining_queries):
            update_status({
                "current_query": query,
                "progress": int((i / len(queries)) * 100)
            })
            
            # Check quota
            quota_info = api_client.get_quota_usage()
            update_status({"quota_used": quota_info['used']})
            
            if quota_info['remaining'] < 4000:
                update_status({
                    "errors": extraction_status["errors"] + ["Insufficient quota remaining"]
                })
                break
            
            try:
                videos = video_extractor.search_videos(query, max_videos=config.videos_per_query)
                all_video_data[query] = videos
                
                update_status({
                    "completed_queries": list(all_video_data.keys()),
                    "videos_collected": sum(len(v) for v in all_video_data.values())
                })
                
                # Save progress
                with open("extraction_progress.json", 'w') as f:
                    json.dump({
                        "completed_queries": list(all_video_data.keys()),
                        "video_data": all_video_data,
                        "last_updated": datetime.now().isoformat()
                    }, f)
                
                await asyncio.sleep(0.1)  # Allow other tasks to run
                
            except QuotaExceededError as e:
                logger.error(f"Quota exceeded during video extraction: {e}")
                update_status({
                    "is_running": False,
                    "quota_exceeded": True,
                    "errors": extraction_status["errors"] + [
                        f"⚠️ QUOTA EXCEEDED: {str(e)}",
                        f"✅ Successfully extracted {len(all_video_data)} queries before limit",
                        "🕒 Quota resets at midnight Pacific Time (PST/PDT)",
                        "💡 Tip: Resume extraction after quota resets - progress is saved!"
                    ]
                })
                break  # Stop extraction
            except Exception as e:
                logger.error(f"Error extracting videos for '{query}': {e}")
                update_status({
                    "errors": extraction_status["errors"] + [f"Error with query '{query}': {str(e)}"]
                })
        
        # Extract channels
        if all_video_data and not extraction_status.get("quota_exceeded", False):
            update_status({"current_query": "Collecting channel data..."})
            try:
                channel_data = channel_extractor.get_channels_for_multiple_queries(all_video_data)
                update_status({"channels_collected": len(channel_data)})
                
                # Export data
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                data_exporter.export_query_videos_to_csv(
                    all_video_data,
                    filename=f'classical_music_videos_{timestamp}.csv'
                )
                data_exporter.export_channels_to_csv(
                    channel_data,
                    filename=f'classical_music_channels_{timestamp}.csv'
                )
                
                quota_info = api_client.get_quota_usage()
                data_exporter.export_summary_report(all_video_data, channel_data, quota_info)
                
            except QuotaExceededError as e:
                logger.error(f"Quota exceeded during channel extraction: {e}")
                update_status({
                    "is_running": False,
                    "quota_exceeded": True,
                    "errors": extraction_status["errors"] + [
                        f"⚠️ QUOTA EXCEEDED during channel collection: {str(e)}",
                        f"✅ Video data collected successfully ({sum(len(v) for v in all_video_data.values())} videos)",
                        "🕒 Quota resets at midnight Pacific Time (PST/PDT)",
                        "💡 Tip: Run extraction again after quota resets to get channel data"
                    ]
                })
            except Exception as e:
                logger.error(f"Error collecting channel data: {e}")
                update_status({
                    "errors": extraction_status["errors"] + [f"Channel collection error: {str(e)}"]
                })
        
        update_status({
            "is_running": False,
            "progress": 100,
            "current_query": None
        })
        
    except Exception as e:
        logger.error(f"Fatal error in extraction task: {e}")
        update_status({
            "is_running": False,
            "errors": extraction_status["errors"] + [f"Fatal error: {str(e)}"]
        })


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/status")
async def get_status():
    """Get current extraction status."""
    status = extraction_status.copy()
    
    # Add quota reset information
    status["quota_reset_info"] = get_quota_reset_time()
    
    return JSONResponse(content=status)


@app.post("/api/extract/start")
async def start_extraction(config: ExtractionConfig, background_tasks: BackgroundTasks):
    """Start data extraction process."""
    if extraction_status["is_running"]:
        raise HTTPException(status_code=400, detail="Extraction already running")
    
    background_tasks.add_task(run_extraction_task, config)
    return {"message": "Extraction started", "status": "running"}


@app.post("/api/extract/stop")
async def stop_extraction():
    """Stop data extraction process."""
    if not extraction_status["is_running"]:
        raise HTTPException(status_code=400, detail="No extraction running")
    
    update_status({"is_running": False, "current_query": None})
    return {"message": "Extraction stop requested", "status": "stopped"}


@app.get("/api/queries")
async def get_queries():
    """Get list of search queries."""
    return {"queries": SEARCH_PHRASES}


@app.get("/api/progress")
async def get_progress():
    """Get detailed progress information."""
    progress = load_progress()
    return {
        "completed_queries": progress.get("completed_queries", []),
        "total_queries": len(SEARCH_PHRASES),
        "completion_percentage": (len(progress.get("completed_queries", [])) / len(SEARCH_PHRASES)) * 100,
        "videos_collected": sum(len(v) for v in progress.get("video_data", {}).values()),
        "last_updated": progress.get("last_updated")
    }


@app.get("/api/analysis/overview")
async def get_analysis_overview():
    """Get overview analytics."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available for analysis")
    
    return analyzer.get_overview_statistics()


@app.get("/api/analysis/queries")
async def get_query_analysis():
    """Get per-query analytics."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available for analysis")
    
    return {"query_statistics": analyzer.get_query_statistics()}


@app.get("/api/analysis/channels/top")
async def get_top_channels(limit: int = 20):
    """Get top channels."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available for analysis")
    
    return {"top_channels": analyzer.get_top_channels(limit)}


@app.get("/api/analysis/temporal")
async def get_temporal_analysis():
    """Get temporal distribution analysis."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available for analysis")
    
    return analyzer.get_temporal_distribution()


@app.get("/api/analysis/distribution")
async def get_distribution_analysis():
    """Get channel distribution analysis."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available for analysis")
    
    return analyzer.get_channel_distribution()


@app.get("/api/analysis/engagement")
async def get_engagement_analysis():
    """Get engagement metrics."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available for analysis")
    
    return analyzer.get_engagement_metrics()


@app.get("/api/analysis/report")
async def get_full_report():
    """Get comprehensive analysis report."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available for analysis")
    
    return analyzer.generate_summary_report()


@app.post("/api/analysis/search")
async def search_videos(request: AnalysisRequest):
    """Search videos with filters."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available for analysis")
    
    results = analyzer.search_videos(
        query=request.query or "",
        channel=request.channel or "",
        limit=request.limit
    )
    return {"results": results, "count": len(results)}


@app.get("/api/analytics/rankings")
async def get_channel_rankings():
    """Get comprehensive channel rankings by multiple metrics."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available")
    
    return analyzer.get_channel_rankings()


@app.get("/api/analytics/videos")
async def get_video_statistics():
    """Get detailed video statistics."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available")
    
    return analyzer.get_video_statistics()


@app.get("/api/analytics/dashboard")
async def get_dashboard_data():
    """Get complete dashboard data with all key metrics."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available")
    
    rankings = analyzer.get_channel_rankings()
    video_stats = analyzer.get_video_statistics()
    overview = analyzer.get_overview_statistics()
    
    return {
        "overview": overview,
        "video_statistics": video_stats,
        "rankings": rankings,
        "top_channels": analyzer.get_top_channels(10)
    }


@app.post("/api/query/custom")
async def fetch_custom_query(request: CustomQueryRequest):
    """Fetch data for a custom search query directly."""
    try:
        api_client = YouTubeAPIClient()
        video_extractor = VideoDataExtractor(api_client)
        channel_extractor = ChannelDataExtractor(api_client)
        
        # Extract videos
        videos = video_extractor.search_videos(request.query, max_videos=request.max_videos)
        
        # Extract channels for these videos
        channel_ids = list(set(video['channelId'] for video in videos if 'channelId' in video))
        channels = {}
        if channel_ids:
            channels = channel_extractor.get_channel_details(channel_ids)
        
        quota_info = api_client.get_quota_usage()
        
        return {
            "query": request.query,
            "videos": videos,
            "channels": list(channels.values()),
            "video_count": len(videos),
            "channel_count": len(channels),
            "quota_used": quota_info['used']
        }
    except QuotaExceededError:
        raise HTTPException(status_code=429, detail="Daily quota exceeded")
    except Exception as e:
        logger.error(f"Error fetching custom query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/videos")
async def get_videos_table(skip: int = 0, limit: int = 50, search: str = ""):
    """Get paginated videos data for table display."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available")
    
    videos_df = analyzer.videos_df
    
    # Apply search filter
    if search:
        videos_df = videos_df[
            videos_df['title'].str.contains(search, case=False, na=False) |
            videos_df['channelTitle'].str.contains(search, case=False, na=False) |
            videos_df['description'].str.contains(search, case=False, na=False)
        ]
    
    total = len(videos_df)
    videos_df = videos_df.iloc[skip:skip+limit]
    
    # Convert to dict and format, replacing NaN with None
    videos = videos_df.fillna('').to_dict('records')
    
    return {
        "data": videos,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@app.get("/api/data/channels")
async def get_channels_table(skip: int = 0, limit: int = 50, search: str = ""):
    """Get paginated channels data for table display."""
    analyzer = DataAnalyzer(data_dir=DATA_DIR)
    if not analyzer.load_latest_data():
        raise HTTPException(status_code=404, detail="No data available")
    
    channels_df = analyzer.channels_df
    
    # Apply search filter
    if search:
        channels_df = channels_df[
            channels_df['title'].str.contains(search, case=False, na=False) |
            channels_df['description'].str.contains(search, case=False, na=False)
        ]
    
    total = len(channels_df)
    channels_df = channels_df.iloc[skip:skip+limit]
    
    # Convert to dict and format, replacing NaN with empty strings
    channels = channels_df.fillna('').to_dict('records')
    
    return {
        "data": channels,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@app.get("/api/files")
async def list_data_files():
    """List available data files."""
    if not os.path.exists(DATA_DIR):
        return {"files": []}
    
    files = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.csv') or filename.endswith('.txt'):
            filepath = os.path.join(DATA_DIR, filename)
            files.append({
                "name": filename,
                "size": os.path.getsize(filepath),
                "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
            })
    
    return {"files": sorted(files, key=lambda x: x['modified'], reverse=True)}


@app.get("/api/files/download/{filename}")
async def download_file(filename: str):
    """Download a data file."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(filepath, filename=filename)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
