# Visualization Troubleshooting Guide

## 🔧 The Problem You Experienced

**Issue:** Agents say they created visualizations but no images appear in the chat.

**Root Cause:** Agents were being conversational instead of actually executing Python code to create files.

## ✅ Solutions Implemented

### 1. **Enhanced Agent Instructions**
- Made visualization creation **mandatory** when requested
- Added exact Python code examples agents must follow
- Removed conversational delays ("would you like to see...")

### 2. **Improved File Detection**
- Timestamp-based detection instead of count-based
- Fallback mechanism for recent files if timing is off
- Better logging to track what's happening

### 3. **Backup Visualization Buttons**
- **📊 Button**: Shows recent visualizations manually
- **⚡ Button**: Force-creates a pie chart if agents fail
- Located in chat header for easy access

### 4. **Direct API Force Creation**
- `/api/force-visualization` endpoint bypasses agents
- Directly executes Python code to create charts
- Guaranteed to work when agents fail

## 🚀 How to Use the Fixed System

### **Method 1: Try the Agents (Preferred)**
1. Ask: "Create a pie chart of ticket categories"
2. Wait for response and check if visualization appears
3. Look for new files in chat bubble

### **Method 2: Use Backup Buttons**
If agents don't create files:
1. Click **📊** to show recent visualizations
2. Click **⚡** to force create a pie chart
3. Both buttons are in the chat header

### **Method 3: Manual File Access**
- Generated files are in `output/` directory
- Access via: http://localhost:7777/static/filename.png
- Check what files exist: click 📊 button

## 🧪 Testing the Fix

### **Quick Test Commands:**
```bash
# Test the API endpoints
python test_api.py

# Test agent directly (if needed)
python simple_viz_test.py

# Create example visualization
python example_viz.py
```

### **Chat Test Phrases:**
- "Create a pie chart of ticket categories"
- "Show me monthly trends as a line chart"
- "Make a visualization of the data"

## 🔍 Debugging Steps

### **If Visualizations Still Don't Appear:**

1. **Check Backend Logs:**
   - Look for "Found X visualizations" messages
   - Check for Python execution errors

2. **Check File System:**
   - Look in `output/` directory for new files
   - Verify file timestamps match request time

3. **Test Force Creation:**
   - Click ⚡ button to bypass agents
   - Should create file directly via API

4. **Check Browser Console:**
   - Look for API errors
   - Verify CORS is working

### **Common Issues:**

| Issue | Cause | Solution |
|-------|--------|----------|
| No files created | Agents not executing Python code | Use ⚡ force button |
| Files exist but not displayed | Detection timing issue | Click 📊 recent files |
| API errors | Backend not running | Restart with `python agent.py` |
| CORS errors | Frontend can't connect | Check localhost:7777 is running |

## 📋 System Status Checklist

- ✅ Backend API running on port 7777
- ✅ Frontend UI running on port 3000  
- ✅ Database connection working
- ✅ Data table loaded with ticket data
- ✅ Matplotlib available for chart creation
- ✅ Output directory exists and writable
- ✅ Static file serving working
- ✅ CORS configured for frontend
- ✅ Fallback visualization buttons added
- ✅ Force creation API endpoint working

## 🎯 Expected Behavior Now

1. **Ask for visualization** → Agent creates file → **Chart appears in chat**
2. **If agent fails** → Click ⚡ → **Chart appears in chat**  
3. **Want to see old charts** → Click 📊 → **Recent charts appear**

The system now has **multiple layers of fallback** to ensure visualizations always work!

## 🔧 Advanced Troubleshooting

### **Agent Not Executing Python Code:**
```python
# Test individual agent
from agent import viz_specialist
response = viz_specialist.run("Create a pie chart and save to output/test.png", stream=False)
# Check if test.png was created
```

### **Force API Direct Test:**
```bash
curl -X POST http://localhost:7777/api/force-visualization \
  -H "Content-Type: application/json" \
  -d '{"type": "pie", "query": "SELECT Category, COUNT(*) FROM data GROUP BY Category"}'
```

### **File Detection Test:**
```python
# Check what files are detected
import requests
response = requests.get("http://localhost:7777/api/visualizations")
print(response.json())
```

## 🎉 Success Indicators

✅ Charts appear directly in chat bubbles
✅ Recent visualizations accessible via 📊 button  
✅ Force creation works via ⚡ button
✅ Multiple fallback methods available
✅ Clear error messages when things fail
✅ Detailed logging for debugging

The visualization pipeline is now **robust and reliable**!