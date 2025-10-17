# YouTube Classical Music Data Extraction - Web Application

A modern, responsive web application for extracting and analyzing YouTube video and channel data, with advanced data visualization and interactive features.

## 🌟 Features

### 1. **Dashboard**
- Real-time statistics display
- Progress tracking with visual indicators
- System status monitoring
- Target tracking (34,000 videos goal)
- Quota usage monitoring (10,000 daily limit)

### 2. **Batch Extraction**
- Extract data for 17 predefined classical music search phrases
- Configurable videos per query (up to 2,000)
- Adjustable quota limits
- Background processing with real-time updates
- Automatic progress saving and resume capability

### 3. **Custom Query Fetch** ⭐ NEW
- Directly fetch data for any YouTube search query
- Specify custom video count (10-500)
- Instant results with summary statistics
- View sample videos with links

### 4. **Advanced Data Tables** ⭐ NEW
- Interactive, sortable tables for videos and channels
- Real-time search and filtering
- Pagination for large datasets
- Direct links to YouTube videos and channels
- Responsive design for all screen sizes

### 5. **Analytics & Visualization**
- **Overview**: Total videos, channels, views, subscribers
- **Top Channels**: Rankings by subscribers with detailed stats
- **Temporal Analysis**: Videos published over time (Chart.js)
- **Engagement Metrics**: Views per video, subscriber ratios

### 6. **File Management**
- List all exported CSV files
- View file sizes and modification dates
- One-click download for all data files

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- YouTube Data API v3 key
- All dependencies from `requirements_api.txt`

### Installation

1. **Install dependencies:**
```powershell
pip install -r requirements_api.txt
```

2. **Configure API key:**
Create a `.env` file in the project root:
```
YOUTUBE_API_KEY=your_actual_api_key_here
```

3. **Start the server:**
```powershell
uvicorn api:app --reload
```

4. **Open your browser:**
Navigate to: `http://localhost:8000`

## 📊 Usage Guide

### Dashboard Page
- View real-time extraction statistics
- Monitor system status (Idle/Running)
- Track progress toward 34,000 video goal
- See quota usage (out of 10,000 daily limit)

### Extraction Page
1. Configure settings:
   - **Videos per Query**: 100-2000 (default: 2000)
   - **Daily Quota Limit**: 1000-50000 (default: 10000)
2. Click **Start Extraction**
3. Monitor progress in real-time
4. Click **Stop** to pause at any time
5. Progress is automatically saved

### Custom Query Page ⭐
1. Enter any YouTube search term (e.g., "Mozart Piano Concerto")
2. Set maximum videos to fetch (10-500)
3. Click **Fetch Data**
4. View results instantly:
   - Total videos found
   - Unique channels discovered
   - Quota used for this query
   - Sample videos with links

### Data Tables Page ⭐
**Videos Table:**
- View all collected videos
- Columns: Title, Channel, Published Date, Video ID
- Search by title, channel, or description
- Click titles to open videos on YouTube

**Channels Table:**
- View all unique channels
- Columns: Name, Subscribers, Views, Videos, Country
- Search by channel name or description
- Click names to open channels on YouTube

**Navigation:**
- Use search box to filter results
- Navigate with Previous/Next buttons
- View total count and current page

### Analysis Page
- **Overview**: High-level statistics
- **Channels**: Top 20 channels by subscribers
- **Temporal**: Time-series visualization of uploads
- **Engagement**: Engagement rate calculations

### Files Page
- Browse all exported CSV files
- See file sizes and dates
- Download individual files

## 🔌 API Endpoints

### Status & Control
- `GET /api/status` - Current extraction status
- `POST /api/extract/start` - Start batch extraction
- `POST /api/extract/stop` - Stop extraction
- `GET /api/progress` - Detailed progress info

### Custom Query ⭐
- `POST /api/query/custom` - Fetch data for any search query
  ```json
  {
    "query": "Beethoven Symphony",
    "max_videos": 100
  }
  ```

### Data Tables ⭐
- `GET /api/data/videos?skip=0&limit=50&search=Mozart` - Paginated videos
- `GET /api/data/channels?skip=0&limit=50&search=Piano` - Paginated channels

### Analytics
- `GET /api/analysis/overview` - Overview statistics
- `GET /api/analysis/channels/top?limit=20` - Top channels
- `GET /api/analysis/temporal` - Temporal distribution
- `GET /api/analysis/engagement` - Engagement metrics

### Files
- `GET /api/files` - List available files
- `GET /api/files/download/{filename}` - Download file

### System
- `GET /health` - Health check
- `GET /api/queries` - List search phrases

## 📁 Data Structure

### Videos CSV
- `videoId`: Unique YouTube video ID
- `title`: Video title
- `description`: Video description
- `publishedAt`: Publication date
- `channelTitle`: Channel name
- `channelId`: Channel ID

### Channels CSV
- `channelId`: Unique channel ID
- `title`: Channel name
- `description`: Channel description
- `subscriberCount`: Total subscribers
- `viewCount`: Total views
- `videoCount`: Total videos
- `country`: Channel country

## 🎨 Technology Stack

### Backend
- **FastAPI** 0.104.1 - Modern Python web framework
- **Uvicorn** 0.24.0 - ASGI server
- **Pandas** 2.1.4 - Data analysis
- **Google API Python Client** - YouTube API integration

### Frontend
- **Bootstrap** 5.3.2 - Responsive CSS framework
- **Chart.js** 4.4.0 - Data visualization
- **Font Awesome** 6.4.2 - Icons
- **Vanilla JavaScript** - Interactive functionality

### Features
- Async/background task processing
- Real-time status polling (5-second intervals)
- Progress persistence (JSON checkpoints)
- Quota management
- Error handling and reporting

## 📱 Responsive Design

The application is fully responsive and optimized for:
- **Desktop**: Full feature set with multi-column layouts
- **Tablet**: Adaptive grid system
- **Mobile**: Single-column layout with touch-friendly controls

## ⚙️ Configuration

### Search Phrases (17 total)
The system extracts data for these classical music queries:
1. Classical music
2. Classical piano
3. Classical symphony
4. Baroque music
5. Mozart piano
6. Beethoven symphony
7. Bach fugue
8. Classical guitar
9. Opera aria
10. Classical violin
11. Chopin nocturne
12. Classical cello
13. Chamber music
14. Orchestral music
15. Piano concerto
16. String quartet
17. Classical composer

### Quota Management
- Each video search costs ~100 quota units
- Channel details cost 1 unit per channel
- Default daily limit: 10,000 units
- Configurable via web interface

## 🛠️ Development

### File Structure
```
├── api.py                  # FastAPI application
├── youtube_client.py       # API client & quota manager
├── video_extractor.py      # Video data extraction
├── channel_extractor.py    # Channel data extraction
├── data_exporter.py        # CSV export functionality
├── data_analyzer.py        # Analytics engine
├── templates/
│   └── index.html          # Main web interface
├── static/
│   ├── app.js              # Frontend JavaScript
│   └── style.css           # Custom styles
├── data/                   # Exported CSV files
├── requirements_api.txt    # Python dependencies
└── .env                    # API key configuration
```

### Running in Development Mode
```powershell
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Running in Production
```powershell
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔍 Troubleshooting

### No data available
- Run extraction from the Extraction page first
- Or use Custom Query to fetch sample data

### API key errors
- Check `.env` file exists
- Verify API key is valid
- Ensure YouTube Data API v3 is enabled

### Quota exceeded
- Wait until next day (resets at midnight Pacific Time)
- Or request quota increase from Google Cloud Console

### Port already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

## 📈 Performance Tips

1. **Batch Extraction**: Use default settings (2000 videos/query) for comprehensive data
2. **Custom Queries**: Use smaller limits (100-200) for quick tests
3. **Tables**: Use search to filter large datasets before browsing
4. **Analytics**: Overview and Channels load fastest; Temporal requires more processing

## 🔒 Security Notes

- Never commit `.env` file to version control
- Keep API keys secure
- Use environment variables in production
- Consider rate limiting for public deployments

## 📝 License

This project is for educational purposes. Respect YouTube's Terms of Service and API usage policies.

## 🤝 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review API documentation
3. Check quota usage in Dashboard
4. Verify `.env` configuration

## 🎯 Roadmap

- [ ] Export to multiple formats (JSON, Excel)
- [ ] Advanced filtering and sorting
- [ ] User authentication
- [ ] Scheduled extraction jobs
- [ ] Email notifications
- [ ] Data comparison across time periods
- [ ] Custom visualization builder

---

**Version**: 2.0.0  
**Last Updated**: October 2025  
**Author**: YouTube Data Extraction Team
