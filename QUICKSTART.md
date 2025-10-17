# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Get Your YouTube API Key

1. Visit https://console.developers.google.com/
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create an API Key under Credentials
5. Copy the API key

## Step 2: Setup

```powershell
# Navigate to project directory
cd "C:\Users\npdim\OneDrive\Documents\MEGA\yt\YouTube-API-Data-Extraction"

# Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
copy .env.example .env

# Edit .env and add your API key
notepad .env
```

In the `.env` file, replace `your_api_key_here` with your actual API key:
```
YOUTUBE_API_KEY=AIzaSyC...your_actual_key...xyz
```

## Step 3: Run

```powershell
python main.py
```

## Step 4: Check Output

Results will be in the `data/` folder:
- `classical_music_videos_*.csv` - All videos (34,000 records)
- `classical_music_channels_*.csv` - All channels (unique)
- `extraction_summary_*.txt` - Summary report

## Important Notes

⏱️ **Timeline**: Due to YouTube's 10,000 daily quota limit, completing all 17 queries will take **7-10 days**. The script automatically:
- Tracks progress
- Stops when approaching quota limit
- Resumes from where it left off when you run it again

🔄 **Daily Routine**: 
1. Run `python main.py` once per day
2. Let it collect ~2-3 queries worth of data
3. Wait for quota reset at midnight Pacific Time
4. Repeat until all 17 queries are complete

📊 **Progress Tracking**: Check `youtube_extraction.log` for detailed progress

## Troubleshooting

**Script won't run?**
```powershell
# Check Python version (needs 3.7+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**API key error?**
- Make sure `.env` file exists in the project root
- Verify the API key is correct (no extra spaces)
- Ensure YouTube Data API v3 is enabled in Google Console

**Quota exceeded?**
- This is normal! Just run the script again after midnight Pacific Time
- Your progress is saved automatically in `extraction_progress.json`

## What Happens Next?

The script will:
1. ✅ Start collecting videos for the first search phrase
2. ✅ Save progress after each phrase
3. ✅ Stop when approaching daily quota limit
4. ✅ Resume from checkpoint when you run it again
5. ✅ Export everything to CSV when complete

## Need Help?

Check the full `README.md` for detailed documentation, or review `youtube_extraction.log` for error details.

Happy data collecting! 🎵
