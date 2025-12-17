# 🧹 Automatic File Cleanup Information

## Current Automatic Cleanup

### ✅ What Gets Deleted Automatically

1. **Original Uploaded Files** - Automatically deleted after processing:
   - **Image files** (`/predict` endpoint): Deleted at line 241 after analysis
   - **Video files** (`/predict_video` endpoint): Deleted at line 535 after analysis  
   - **Reverse search files** (`/reverse_search` endpoint): Deleted at line 362 after search

### ❌ What Does NOT Get Deleted Automatically (Before Fix)

- **Heatmap files** - These were accumulating in `uploads/image_heatmaps/` and `uploads/video_heatmaps/`
- **Old generated files** - No cleanup for files older than a certain age

---

## 🆕 New Automatic Cleanup Added

### Automatic Heatmap Cleanup

I've added automatic cleanup functionality that:

1. **Runs on Server Startup**: Cleans up old heatmaps when the Flask app starts
2. **Runs After Each Heatmap Generation**: Automatically cleans old heatmaps after creating a new one
3. **Deletes Files Older Than 1 Hour**: Configurable age threshold (default: 1 hour)

### How It Works

```python
def cleanup_old_heatmaps(max_age_hours=1):
    """Delete heatmap files older than max_age_hours"""
    # Deletes files in:
    # - uploads/image_heatmaps/*_heatmap.png
    # - uploads/video_heatmaps/**/*.png
```

### Manual Cleanup Endpoint

You can also manually trigger cleanup via API:

```bash
POST http://localhost:5000/cleanup
```

This will delete all heatmap files older than 1 hour.

---

## 📝 Configuration

### Change Cleanup Age

To change how old files must be before deletion, modify the `max_age_hours` parameter:

```python
# In app.py, change this:
cleanup_old_heatmaps(max_age_hours=1)  # 1 hour

# To something like:
cleanup_old_heatmaps(max_age_hours=24)  # 24 hours
```

---

## 🔍 File Lifecycle

### Image Detection Flow
1. User uploads image → Saved temporarily
2. Model processes image → Generates heatmap
3. **Original image deleted** ✅ (line 241)
4. **Old heatmaps cleaned** ✅ (after heatmap generation)
5. Heatmap served to user → Stays for 1 hour, then auto-deleted

### Video Detection Flow
1. User uploads video → Saved temporarily
2. API processes video → Generates frame heatmaps
3. **Original video deleted** ✅ (line 535)
4. **Old heatmaps cleaned** ✅ (on next image detection or startup)

---

## 📊 Cleanup Summary

| File Type | Auto-Delete? | When? | Age Threshold |
|-----------|--------------|-------|---------------|
| Uploaded Images | ✅ Yes | After processing | Immediate |
| Uploaded Videos | ✅ Yes | After processing | Immediate |
| Image Heatmaps | ✅ Yes | After generation + startup | 1 hour |
| Video Heatmaps | ✅ Yes | On startup + periodic | 1 hour |

---

## 🚀 Usage

### Automatic (No Action Required)
- Cleanup runs automatically when:
  - Server starts
  - New heatmap is generated

### Manual Cleanup
```bash
# Using curl
curl -X POST http://localhost:5000/cleanup

# Using Python requests
import requests
requests.post('http://localhost:5000/cleanup')
```

---

## ⚙️ Technical Details

### Cleanup Function Location
- **File**: `app.py`
- **Function**: `cleanup_old_heatmaps(max_age_hours=1)`
- **Called at**:
  - Server startup (line ~47)
  - After heatmap generation (line ~156)

### Files Scanned
- `uploads/image_heatmaps/*_heatmap.png`
- `uploads/video_heatmaps/**/*.png` (recursive)

### Error Handling
- Cleanup errors are logged but don't crash the server
- Individual file deletion errors are caught and logged

---

*Last Updated: 2025-01-27*
*Cleanup Feature: Active*

