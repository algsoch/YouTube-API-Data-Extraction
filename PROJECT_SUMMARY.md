# 🎵 YouTube Classical Music Data Extraction - Complete System

## ✅ PROJECT STATUS: READY TO RUN

All components have been created, tested, and validated. The system is ready for data collection.

---

## 📁 Project Structure

```
YouTube-API-Data-Extraction/
│
├── 📄 Core Scripts
│   ├── main.py                    # Main orchestration script
│   ├── youtube_client.py          # API client with quota management
│   ├── video_extractor.py         # Video data extraction
│   ├── channel_extractor.py       # Channel data extraction
│   └── data_exporter.py           # CSV export functionality
│
├── 🛠️ Helper Scripts
│   ├── validate_setup.py          # Pre-flight validation checker
│   └── run_extraction.ps1         # PowerShell runner with error handling
│
├── 📚 Documentation
│   ├── README.md                  # Comprehensive documentation
│   ├── QUICKSTART.md             # 5-minute setup guide
│   ├── QUOTA_PLANNING.md         # Timeline & quota breakdown
│   └── PROJECT_SUMMARY.md        # This file
│
├── ⚙️ Configuration
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment template
│   ├── .env                     # Your API key (already configured)
│   └── .gitignore              # Git ignore rules
│
└── 📊 Output (auto-generated)
    ├── data/                    # CSV output directory
    │   ├── classical_music_videos_*.csv
    │   ├── classical_music_channels_*.csv
    │   └── extraction_summary_*.txt
    ├── extraction_progress.json # Progress checkpoint
    └── youtube_extraction.log   # Detailed execution log
```

---

## 🎯 What This System Does

### Phase 1: Video Collection
- Searches YouTube for 17 classical music phrases
- Collects 2,000 most recent videos per phrase
- Total: **34,000 videos**
- Captures: videoId, title, description, publishedAt, channelTitle, channelId

### Phase 2: Channel Collection
- Extracts unique channel IDs from all videos
- Fetches complete profile for each channel
- Expected: **2,000-5,000 unique channels**
- Captures: title, description, publishedAt, country, customUrl, viewCount, subscriberCount, videoCount, hiddenSubscriberCount, channelUrl

### Phase 3: Data Export
- Exports all data to clean CSV files
- UTF-8 encoding for international characters
- Includes summary report with statistics

---

## 🚀 Quick Start

### Option A: PowerShell Script (Recommended)
```powershell
.\run_extraction.ps1
```

### Option B: Direct Python
```powershell
python main.py
```

### Option C: With Validation First
```powershell
python validate_setup.py
python main.py
```

---

## ⏱️ Expected Timeline

| Scenario | Timeline | Details |
|----------|----------|---------|
| **Default Quota** | 8-10 days | 10,000 units/day, ~2 queries per day |
| **Increased Quota** | 2-3 days | 50,000 units/day (request from Google) |
| **Multiple API Keys** | 2-4 days | Rotate keys, ensure ToS compliance |

### Daily Routine
1. Run script once per day (after midnight Pacific Time)
2. Script collects 2-3 queries automatically
3. Stops when approaching quota limit
4. Saves progress
5. Repeat next day until complete

---

## 📊 Key Features

### ✅ Quota Management
- Real-time quota tracking
- Automatic stopping before limit
- Smart cost calculation per operation

### ✅ Progress Tracking
- Saves after each completed query
- Resumes from checkpoint automatically
- No data loss on interruption

### ✅ Error Handling
- Graceful handling of API errors
- Automatic retry logic
- Detailed error logging

### ✅ Rate Limiting
- 1 request per second to avoid throttling
- Configurable delays between operations
- Respects YouTube API best practices

---

## 📈 Search Phrases

All 17 phrases configured:

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

---

## 🛠️ Technical Stack

- **Language**: Python 3.7+ (tested with 3.13.9)
- **API**: YouTube Data API v3
- **Dependencies**:
  - google-api-python-client 2.108.0
  - google-auth 2.25.2
  - pandas 2.1.4
  - python-dotenv 1.0.0

---

## 📋 Pre-flight Checklist

Run `python validate_setup.py` to verify:

- ✅ Python 3.7+ installed
- ✅ All required packages installed
- ✅ .env file configured with valid API key
- ✅ All project files present
- ✅ Output directory created

---

## 📤 Deliverables

### 1. Videos CSV
**File**: `classical_music_videos_YYYYMMDD_HHMMSS.csv`

**Columns**:
- searchQuery
- videoId
- title
- description
- publishedAt
- channelTitle
- channelId

**Rows**: ~34,000 (2,000 per query × 17 queries)

### 2. Channels CSV
**File**: `classical_music_channels_YYYYMMDD_HHMMSS.csv`

**Columns**:
- channelId
- title
- description
- publishedAt
- country
- customUrl
- viewCount
- subscriberCount
- videoCount
- hiddenSubscriberCount
- channelUrl

**Rows**: ~2,000-5,000 unique channels

### 3. Summary Report
**File**: `extraction_summary_YYYYMMDD_HHMMSS.txt`

Contains:
- Video counts per query
- Unique channel count
- Quota usage statistics
- Timestamp information

---

## 🔍 Monitoring Progress

### Real-time Console Output
The script provides live updates:
- Current query being processed
- Videos collected so far
- Quota usage
- Estimated time remaining

### Log File
```powershell
Get-Content youtube_extraction.log -Tail 50
```

### Progress File
```powershell
Get-Content extraction_progress.json
```

---

## 🚨 Important Notes

### Quota Limits
- Default: 10,000 units/day
- Resets: Midnight Pacific Time
- Can be increased via Google Cloud Console

### Data Freshness
- Videos sorted by most recent (`order=date`)
- Data reflects state at time of extraction
- Can be re-run for updated data

### API Key Security
- Keep `.env` file secure
- Never commit to version control
- Can rotate keys if compromised

### Terms of Service
- Ensure compliance with YouTube ToS
- Respect rate limits
- Don't abuse API access

---

## 🆘 Troubleshooting

### Script won't run
```powershell
python validate_setup.py
```

### API key issues
1. Check `.env` file exists
2. Verify API key is correct
3. Ensure YouTube Data API v3 is enabled

### Quota exceeded
- Normal! Wait for reset at midnight PT
- Progress is saved automatically
- Run script again after reset

### Import errors
```powershell
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Support Resources

### Documentation
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick setup guide
- `QUOTA_PLANNING.md` - Timeline planning

### Logs
- `youtube_extraction.log` - Detailed execution log
- Console output - Real-time progress

### YouTube API
- [Official Documentation](https://developers.google.com/youtube/v3)
- [Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)
- [API Console](https://console.developers.google.com/)

---

## 🎉 Next Steps

1. **Verify Setup**:
   ```powershell
   python validate_setup.py
   ```

2. **Start Extraction**:
   ```powershell
   python main.py
   ```

3. **Monitor Progress**:
   - Check console output
   - Review `youtube_extraction.log`
   - Watch `data/` folder for outputs

4. **Daily Routine** (for 8-10 days):
   - Run script once per day
   - Let it collect 2-3 queries
   - Check progress
   - Repeat until complete

5. **Completion**:
   - Review CSV files in `data/` folder
   - Check summary report
   - Analyze collected data

---

## ✨ System Status

- **Code Status**: ✅ Complete and tested
- **Syntax Check**: ✅ All files compile successfully
- **Validation**: ✅ All pre-flight checks passed
- **Dependencies**: ✅ Installed and verified
- **Configuration**: ✅ API key configured
- **Ready to Run**: ✅ YES

---

## 📅 Estimated Completion

**Start Date**: Today (October 18, 2025)
**Expected Completion**: October 26-28, 2025 (8-10 days)
**Total Data**: 34,000 videos + 2,000-5,000 channels

---

**🎵 Happy Data Collecting! 🎵**

The system is fully automated and will handle everything. You only need to run it once per day for the next 8-10 days. All deliverables will be automatically generated in CSV format as specified.
