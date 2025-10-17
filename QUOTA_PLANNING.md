# YouTube API Quota Planning & Timeline

## Understanding YouTube API Quotas

### Daily Quota Limit
- **Default limit**: 10,000 units per day
- **Reset time**: Midnight Pacific Time (PST/PDT)
- **Can be increased**: Request from Google Cloud Console (may take days for approval)

### Operation Costs

| Operation | Cost (units) | Description |
|-----------|--------------|-------------|
| Search | 100 | Each search request |
| Videos.list | 1 | Get video details |
| Channels.list | 1 | Get channel details |

### Per-Query Breakdown

To fetch 2,000 videos for one search phrase:

- **Search requests**: ~40 requests (50 results per page × 40 pages)
  - Cost: 40 × 100 = **4,000 units**
- **Channel requests**: ~varies (depends on unique channels, batched in groups of 50)
  - Estimated: 20-50 units per query

**Total per query**: ~4,000-4,050 units

## Project Requirements

### Total Data to Collect
- **17 search phrases** × 2,000 videos each = **34,000 videos**
- **Unique channels**: Estimated 2,000-5,000 channels
- **Total quota needed**: ~68,000-70,000 units

### Timeline Estimate

With 10,000 daily quota:

| Day | Queries | Videos | Quota Used | Cumulative Progress |
|-----|---------|--------|------------|---------------------|
| 1 | 2 | 4,000 | ~8,100 | 11.8% |
| 2 | 2 | 4,000 | ~8,100 | 23.5% |
| 3 | 2 | 4,000 | ~8,100 | 35.3% |
| 4 | 2 | 4,000 | ~8,100 | 47.1% |
| 5 | 2 | 4,000 | ~8,100 | 58.8% |
| 6 | 2 | 4,000 | ~8,100 | 70.6% |
| 7 | 2 | 4,000 | ~8,100 | 82.4% |
| 8 | 2 | 4,000 | ~8,100 | 94.1% |
| 9 | 1 | 2,000 | ~4,100 | 100% (videos) |
| 10 | - | - | ~2,500 | 100% (channels) |

**Expected completion**: 8-10 days

### Optimizing Timeline

#### Option 1: Request Quota Increase
1. Go to Google Cloud Console
2. Navigate to YouTube Data API v3 quotas
3. Request increase (e.g., to 50,000 units/day)
4. If approved, complete entire project in ~2 days

#### Option 2: Use Multiple API Keys
- Create multiple Google Cloud projects
- Each gets 10,000 units/day
- Rotate keys in `.env` file
- ⚠️ Ensure compliance with YouTube ToS

#### Option 3: Reduce Videos Per Query
- Change `VIDEOS_PER_QUERY` from 2000 to 1000
- Complete project in ~4-5 days
- Collect 17,000 total videos instead of 34,000

## Daily Routine

### Morning (After Quota Reset)

```powershell
# Run the extraction
python main.py
```

The script will:
1. Resume from last checkpoint
2. Process 2-3 queries
3. Stop when approaching quota limit
4. Save progress automatically

### Monitoring Progress

Check log file:
```powershell
Get-Content youtube_extraction.log -Tail 20
```

Check progress file:
```powershell
Get-Content extraction_progress.json
```

View current quota usage in console output or log file.

## Quota Management Features

The script automatically:
- ✅ Tracks quota usage in real-time
- ✅ Stops before exceeding daily limit
- ✅ Saves progress after each query
- ✅ Allows resumption the next day
- ✅ Warns when quota is running low

## Expected Output Size

### Video CSV
- **Rows**: ~34,000 (2,000 per query × 17 queries)
- **Columns**: 7 (searchQuery, videoId, title, description, publishedAt, channelTitle, channelId)
- **File size**: ~15-25 MB (depends on description lengths)

### Channel CSV
- **Rows**: ~2,000-5,000 (unique channels)
- **Columns**: 11 (channelId, title, description, publishedAt, country, customUrl, viewCount, subscriberCount, videoCount, hiddenSubscriberCount, channelUrl)
- **File size**: ~2-5 MB

## Troubleshooting Quota Issues

### "Quota Exceeded" Error

**Cause**: Hit daily limit

**Solution**: 
```
Wait until midnight Pacific Time, then run:
python main.py
```

Progress is saved, will resume automatically.

### "Insufficient Quota" Warning

**Cause**: Not enough quota left to complete current query

**Solution**: Script stops automatically. Run again after quota reset.

### Check Current Quota Usage

From Google Cloud Console:
1. Go to APIs & Services → Dashboard
2. Click YouTube Data API v3
3. View "Queries per day" chart

## Best Practices

1. **Run Daily**: Set a reminder to run the script daily after midnight PT
2. **Monitor Logs**: Check logs to ensure progress
3. **Backup Progress**: The `extraction_progress.json` file contains your checkpoint
4. **Don't Delete Progress File**: Until extraction is complete
5. **Save API Key**: Keep `.env` file secure and backed up

## Alternative Strategies

### Strategy A: Quick Collection (Higher Quota)
- Request 50,000 units/day quota
- Complete in 2 days
- Best for urgent needs

### Strategy B: Steady Collection (Default)
- Use default 10,000 units/day
- Complete in 8-10 days
- No special approvals needed

### Strategy C: Targeted Collection
- Start with high-priority queries
- Modify `SEARCH_PHRASES` list order
- Get important data first

## Questions?

For quota-related questions:
- [YouTube API Quota Documentation](https://developers.google.com/youtube/v3/getting-started#quota)
- [Request Quota Increase](https://support.google.com/youtube/contact/yt_api_form)

For script issues:
- Check `youtube_extraction.log`
- Review `README.md`
- Run `python validate_setup.py`
