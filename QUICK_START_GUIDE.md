# 🚀 Quick Start Guide - YouTube Data Extraction Web App

## Current Status: ✅ Server Running

Your web application is running at: **http://127.0.0.1:8000**

---

## 📊 Understanding the Dashboard

### Why You See "0" Everywhere?
**Answer:** You haven't run any extraction yet! This is normal for a fresh start.

The dashboard shows:
- **Videos Collected: 0** (Target: 34,000) - No extraction run yet
- **Channels: 0** - No data collected
- **Completed Queries: 0 / 17** - Haven't started processing search phrases
- **Quota Used: 0** - No API calls made
- **Status: System Idle** - Ready to start!

---

## 🎯 How to Get Started

### Option 1: Quick Test with Custom Query (Recommended for First Time)

This is the **fastest way** to test the system without using much quota!

1. **Click** on "Custom Query" in the navigation bar
2. **Enter** a search term (e.g., "Mozart Piano Concerto")
3. **Set** max videos to **50** (uses ~100 quota units)
4. **Click** "Fetch Data"
5. **View** instant results!

**Why start here?**
- ✅ Uses minimal quota (~100 units)
- ✅ See results in seconds
- ✅ Test if API key works
- ✅ No long wait times

---

### Option 2: Full Batch Extraction (For Complete Dataset)

This extracts data for all 17 classical music search phrases.

1. **Click** on "Extraction" in the navigation bar
2. **Configure Settings**:
   - Videos per Query: **2000** (default - collects 34,000 total videos)
   - Daily Quota Limit: **10000** (default - safe limit)
3. **Click** "Start Extraction"
4. **Monitor** progress in real-time:
   - Watch the progress bar
   - See current query being processed
   - Check quota usage

**Time Required:**
- Approximately **2-3 hours** for full extraction
- Depends on API response times

**What Gets Extracted:**
- 17 search phrases × 2,000 videos = **34,000 videos**
- Unique channel data for all channels found
- Exported as CSV files in the `data/` folder

---

## 📋 Step-by-Step: Your First Extraction

### Recommended First-Time Flow:

#### Step 1: Test with Custom Query
```
1. Go to "Custom Query" page
2. Enter: "Beethoven Symphony"
3. Max videos: 100
4. Click "Fetch Data"
5. ✅ Verify it works!
```

#### Step 2: View the Data Tables
```
1. Go to "Data Tables" page (if you ran extraction)
2. Click "Videos" to see video data
3. Click "Channels" to see channel data
4. Use search box to filter
5. Click titles to open on YouTube
```

#### Step 3: Run Full Extraction
```
1. Go to "Extraction" page
2. Keep default settings (2000 videos/query)
3. Click "Start Extraction"
4. Go back to "Dashboard" to monitor
5. Wait for completion (or stop anytime)
```

#### Step 4: Explore Analysis
```
1. Go to "Analysis" page
2. Click "Overview" - See total stats
3. Click "Channels" - Top channels by subscribers
4. Click "Temporal" - Videos over time chart
5. Click "Engagement" - Engagement metrics
```

#### Step 5: Download Files
```
1. Go to "Files" page
2. See all exported CSV files
3. Click "Download" to get files
4. Open in Excel/Google Sheets
```

---

## ⚠️ Important: Quota Management

### Understanding Quota:
- **Daily Limit**: 10,000 units (resets midnight Pacific Time)
- **Search Cost**: 100 units per query
- **Video Details**: 1 unit per batch (50 videos)
- **Channel Details**: 1 unit per batch (50 channels)

### Quota Calculator:

**Custom Query (100 videos):**
- 1 search = 100 units
- 100 videos ÷ 50 = 2 batches = 2 units
- **Total: ~102 units** ✅ Very safe!

**Full Extraction (34,000 videos):**
- 17 searches = 1,700 units
- 34,000 videos ÷ 50 = 680 units
- ~3,000 channels ÷ 50 = 60 units
- **Total: ~2,440 units** ✅ Fits in daily limit!

### What If Quota Runs Out?

The app will:
1. ⚠️ Stop extraction automatically
2. ✅ Save all collected data
3. 🕒 Show when quota resets
4. 💡 Tell you how to resume

**No data is lost!** Just start again after quota resets.

---

## 🔧 Troubleshooting

### "No data available yet"
**Cause:** Haven't run extraction  
**Solution:** Go to "Extraction" or "Custom Query" page and fetch data

### "Failed to load analysis"
**Cause:** No CSV files in `data/` folder  
**Solution:** Run extraction first, then check Analysis page

### "API key errors"
**Cause:** Invalid or missing API key  
**Solution:** Check your `.env` file has correct `YOUTUBE_API_KEY`

### "Quota exceeded"
**Cause:** Used all 10,000 daily units  
**Solution:** Wait until midnight Pacific Time, or resume tomorrow

### Server not responding
**Cause:** Server stopped  
**Solution:** Run `uvicorn api:app --reload` in terminal

---

## 📂 Where Is My Data?

After extraction completes, you'll find files in the `data/` folder:

```
data/
├── classical_music_videos_20251018_023045.csv    (All videos)
├── classical_music_channels_20251018_023045.csv  (All channels)
└── extraction_summary_20251018_023045.txt        (Summary report)
```

### File Contents:

**Videos CSV:**
- videoId, title, description
- publishedAt, channelTitle, channelId

**Channels CSV:**
- channelId, title, description
- subscriberCount, viewCount, videoCount
- country, customUrl

---

## 🎨 Features Overview

### 🏠 Dashboard
- Real-time statistics
- Progress tracking
- Quota monitoring
- System status

### 📥 Extraction
- Batch extraction (17 queries)
- Configurable settings
- Background processing
- Auto-save progress

### 🔍 Custom Query
- Fetch any search term
- Quick results
- Minimal quota usage
- Perfect for testing

### 📊 Data Tables
- Interactive video table
- Interactive channel table
- Search & filter
- Pagination
- Direct YouTube links

### 📈 Analysis
- Overview statistics
- Top channels ranking
- Temporal distribution
- Engagement metrics
- Chart.js visualizations

### 📁 Files
- List all exports
- File sizes & dates
- One-click downloads

---

## 💡 Pro Tips

### Tip 1: Start Small
Use Custom Query with 50-100 videos to test before running full extraction.

### Tip 2: Monitor Dashboard
Keep Dashboard open in another tab to watch progress in real-time.

### Tip 3: Save Progress
The app auto-saves every query. You can stop/start anytime!

### Tip 4: Peak Hours
Run extraction during off-peak hours (night/weekend) for faster API responses.

### Tip 5: Data Tables
Use Data Tables to verify data quality before downloading files.

### Tip 6: Multiple Searches
After full extraction, use Custom Query for additional searches without affecting saved data.

---

## ⏰ Typical Timeline

### Quick Test (Custom Query)
- **Setup**: 10 seconds
- **Fetch**: 5-10 seconds
- **Review**: 2 minutes
- **Total**: ~3 minutes ⚡

### Full Extraction
- **Setup**: 30 seconds
- **Video Extraction**: 1-2 hours
- **Channel Extraction**: 30-60 minutes
- **Export**: 5 minutes
- **Total**: ~2-3 hours ⏱️

---

## 🎯 Your Next Steps

### Right Now:
1. ✅ Server is running at http://127.0.0.1:8000
2. ✅ API key is configured (from .env)
3. ✅ All features ready to use

### Choose Your Path:

**Path A: Test First (Recommended)**
```
Custom Query → Enter "Mozart Piano" → 100 videos → Fetch
↓
View results → Check if API works → Verify data quality
↓
Go to Extraction → Start full extraction
```

**Path B: Go All-In**
```
Extraction page → Keep defaults → Start Extraction
↓
Wait 2-3 hours → Check Dashboard → Download from Files page
```

---

## 📞 Need Help?

### Check These First:
1. **Dashboard** - Current status and errors
2. **Terminal** - Server logs and error messages  
3. **QUOTA_MANAGEMENT.md** - Quota handling info
4. **README_WEBAPP.md** - Complete documentation

### Common Questions:

**Q: How long does extraction take?**  
A: 2-3 hours for full 34,000 videos

**Q: Can I stop and resume?**  
A: Yes! Progress is auto-saved

**Q: What if I run out of quota?**  
A: App stops gracefully, shows reset time

**Q: Can I extract different queries?**  
A: Yes! Use Custom Query page

**Q: Where are CSV files?**  
A: In the `data/` folder

---

## 🚀 Ready to Start?

1. **Open** http://127.0.0.1:8000 in your browser
2. **Click** "Custom Query" for quick test
3. **Or Click** "Extraction" for full dataset
4. **Enjoy** your classical music data! 🎵

---

**Last Updated**: October 18, 2025  
**Status**: ✅ System Ready  
**Server**: Running on http://127.0.0.1:8000
