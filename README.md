# 🎵 YouTube Classical Music Data Extraction & Analytics Platform

**Automated data extraction, analysis, and visualization** for YouTube classical music content using the official YouTube Data API v3.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

---

## Overview

A **professional web application** that fetches 2,000 videos per search query across 17 classical music works, providing comprehensive analytics, interactive visualizations, and export-ready CSV data. Perfect for researchers, marketers, and data analysts in the classical music space.

**Live Demo**: `http://localhost:8000` (when running)

---

## ✨ Key Features

### 🎯 Core Capabilities
- **Automated Extraction**: 2,000 videos × 17 queries = 34,000 total videos
- **Channel Analytics**: Complete profile data (subscribers, views, country, videos)
- **Web Interface**: 6-page responsive dashboard with Bootstrap 5.3
- **REST API**: 20+ endpoints for programmatic access
- **CSV Export**: Clean, structured data files ready for Excel/BI tools
- **Docker Ready**: One-command deployment with docker-compose

### 📊 Advanced Analytics
- **🥇 Most Subscribed**: Top 20 channels by subscriber count
- **👁️ Most Viewed**: Channels ranked by total views
- **🎬 Most Prolific**: Highest video output producers
- **🌱 Emerging Talent**: Hidden gems with growth potential
- **🌍 Geographic Analysis**: Channel distribution by country
- **📈 Temporal Trends**: Publication patterns over time
- **🔍 Interactive Charts**: Real-time visualization with Chart.js

### ⚡ Smart Features
- **Quota Management**: Automatic API quota tracking with reset timers
- **Progress Tracking**: Real-time extraction status and metrics
- **Custom Queries**: Ad-hoc searches for any YouTube content
- **Search & Pagination**: Filter through thousands of records instantly
- **Background Processing**: Non-blocking data collection
- **Error Recovery**: Graceful handling of quota limits and API errors

---

## 🚀 Quick Start

### Option 1: Run Locally (Python)

- ✅ **Quota-Aware**: Intelligent quota management to stay within YouTube's 10,000 daily units
- ✅ **Rate-Limited**: Respectful API usage with automatic rate limiting
- ✅ **Resume Capability**: Automatic progress saving and resumption if interrupted
- ✅ **Comprehensive Logging**: Detailed logs of all operations
- ✅ **Clean CSV Export**: Well-formatted CSV files with UTF-8 encoding
- ✅ **Error Handling**: Robust error handling with graceful degradation

## Data Collected

### Video Data (2,000 per search phrase)
- `videoId` - Unique YouTube video identifier
- `title` - Video title
- `description` - Video description
- `publishedAt` - Publication timestamp
- `channelTitle` - Name of the channel
- `channelId` - Unique channel identifier
- `searchQuery` - Which search phrase found this video

### Channel Data (unique channels only)
- `channelId` - Unique channel identifier
- `title` - Channel name
- `description` - Channel description
- `publishedAt` - Channel creation date
- `country` - Channel's country
- `customUrl` - Custom channel URL
- `viewCount` - Total channel views
- `subscriberCount` - Number of subscribers
- `videoCount` - Total videos on channel
- `hiddenSubscriberCount` - Whether subscriber count is hidden
- `channelUrl` - Full YouTube channel URL

## Search Phrases

The tool collects data for these 17 classical music works:

1. Beethoven Symphony
2. Handel Messiah
3. Mozart Requiem
4. Mozart Coronation Mass
5. Bach St Matthew Passion
6. Bach St John Passion
7. Brahms A German Requiem
8. Haydn The Creation
9. Haydn The Seasons
10. Faure Requiem
11. Faure Cantique de Jean Racine
12. Vivaldi Gloria
13. Bach Magnificat
14. Mendelssohn Elijah
15. Schubert Mass
16. Beethoven Missa Solemnis
17. Mozart Ave Verum

## Prerequisites

- Python 3.7 or higher
- YouTube Data API v3 key
- Internet connection

## Installation

### 1. Clone or Download This Repository

```powershell
cd "C:\Users\npdim\OneDrive\Documents\MEGA\yt\YouTube-API-Data-Extraction"
```

### 2. Create Virtual Environment (Recommended)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you encounter execution policy errors on Windows:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Get YouTube API Key

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select existing one
3. Enable **YouTube Data API v3**
4. Create credentials (API Key)
5. Copy your API key

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```powershell
copy .env.example .env
```

Edit `.env` and add your API key:
```
YOUTUBE_API_KEY=your_actual_api_key_here
```

## Usage

### Run the Extraction

```powershell
python main.py
```

The script will:
1. Initialize the YouTube API client
2. Collect 2,000 most recent videos for each search phrase
3. Extract unique channel IDs from all videos
4. Fetch detailed channel information
5. Export data to CSV files in the `data/` directory
6. Generate a summary report

### Output Files

All files are saved in the `data/` directory with timestamps:

- `classical_music_videos_YYYYMMDD_HHMMSS.csv` - All video data
- `classical_music_channels_YYYYMMDD_HHMMSS.csv` - All channel data
- `extraction_summary_YYYYMMDD_HHMMSS.txt` - Summary report
- `youtube_extraction.log` - Detailed execution log

### Resume After Interruption

If the script is interrupted or quota is exhausted, it automatically saves progress. Simply run the script again:

```powershell
python main.py
```

It will resume from where it left off, skipping already-completed queries.

### Quota Management

YouTube Data API v3 has a **10,000 units per day** quota limit that resets at midnight Pacific Time.

**Operation Costs:**
- Search request: 100 units
- Video details: 1 unit
- Channel details: 1 unit

**Estimated Usage:**
- 2,000 videos per query ≈ 40 search requests = 4,000 units
- 17 queries ≈ 68,000 units total
- **You'll need approximately 7-10 days** to complete all 17 queries

The script monitors quota usage and stops automatically when nearing the limit, saving progress for the next day.

## Project Structure

```
YouTube-API-Data-Extraction/
├── main.py                  # Main orchestration script
├── youtube_client.py        # API client with quota management
├── video_extractor.py       # Video data extraction logic
├── channel_extractor.py     # Channel data extraction logic
├── data_exporter.py         # CSV export functionality
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── data/                   # Output directory (created automatically)
│   ├── classical_music_videos_*.csv
│   ├── classical_music_channels_*.csv
│   └── extraction_summary_*.txt
├── extraction_progress.json # Progress tracker (auto-generated)
└── youtube_extraction.log   # Execution log (auto-generated)
```

## Troubleshooting

### "YouTube API key not provided" Error

**Solution:** Ensure your `.env` file exists and contains `YOUTUBE_API_KEY=your_key_here`

### Quota Exceeded Errors

**Solution:** Wait until midnight Pacific Time for quota reset. The script will automatically resume.

### Rate Limit Errors

**Solution:** The script includes built-in rate limiting (1 request/second). If you still encounter issues, the script will handle them gracefully.

### Import Errors

**Solution:** Ensure all dependencies are installed:
```powershell
pip install -r requirements.txt
```

### Virtual Environment Issues (Windows)

If activation fails:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

## Timeline Expectations

Given the 10,000 daily quota limit:

- **Day 1-2**: Complete ~2-3 queries (4,000 units each)
- **Day 3-7**: Continue collecting remaining queries
- **Day 7-10**: Complete all 17 queries and channel data collection

The exact timeline depends on:
- Your specific quota limit (can be increased by requesting from Google)
- Number of results returned per query
- API response times

## Advanced Usage

### Modify Search Phrases

Edit the `SEARCH_PHRASES` list in `main.py`:

```python
SEARCH_PHRASES = [
    "Your Custom Query 1",
    "Your Custom Query 2",
    # ...
]
```

### Change Videos Per Query

Modify the `VIDEOS_PER_QUERY` constant in `main.py`:

```python
VIDEOS_PER_QUERY = 1000  # Default is 2000
```

### Adjust Quota Limit

If you have a higher quota limit, update the client initialization in `main.py`:

```python
api_client = YouTubeAPIClient(daily_quota=50000)  # Default is 10000
```

## Data Format

### Videos CSV Example

```csv
searchQuery,videoId,title,description,publishedAt,channelTitle,channelId
Beethoven Symphony,dQw4w9WgXcQ,Beethoven Symphony No. 9,...,2024-10-15T10:30:00Z,Classic FM,UC...
```

### Channels CSV Example

```csv
channelId,title,description,publishedAt,country,customUrl,viewCount,subscriberCount,videoCount,hiddenSubscriberCount,channelUrl
UC...,Classic FM,The world's greatest...,2006-05-01T00:00:00Z,GB,@classicfm,50000000,1500000,5000,False,https://www.youtube.com/channel/UC...
```

## Contributing

Feel free to submit issues or pull requests to improve this tool.

## License

This project is provided as-is for educational and research purposes. Please ensure compliance with YouTube's Terms of Service and API usage policies.

## Support

For issues related to:
- **YouTube API**: Check [YouTube Data API documentation](https://developers.google.com/youtube/v3)
- **This tool**: Review logs in `youtube_extraction.log` or create an issue

## Acknowledgments

- YouTube Data API v3 by Google
- Python libraries: google-api-python-client, pandas, python-dotenv

---

**Note**: This tool is designed for research and educational purposes. Always respect YouTube's Terms of Service and rate limits.
