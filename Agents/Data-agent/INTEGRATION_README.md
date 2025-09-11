# Data Agent Visualization System

An integrated chatbot interface for data analysis with real-time visualization display.

## 🚀 Quick Start

1. **Start the integrated system:**
   ```bash
   python start_system.py
   ```

2. **Open the chat interface:**
   - Navigate to: http://localhost:3000
   - The modern chat UI will connect to your data agents

3. **Ask questions and get visualizations:**
   - "Show me monthly ticket trends"
   - "Create a chart of ticket categories" 
   - "What insights can you provide about our support data?"

## 🏗️ System Architecture

```
Frontend (Next.js)     ←→     Custom FastAPI     ←→     Agent OS     ←→     Data Agents
   Port 3000                      Port 7777                                    (Analysis Team)
                                      ↕
                               Static File Server
                               (serves visualizations)
```

## 🔧 Features

### ✅ Completed Integration
- **Real-time Chat**: Direct connection to Agent OS through custom API
- **Inline Visualizations**: Charts and dashboards display directly in chat
- **Static File Serving**: Automatic serving of generated HTML/PNG files
- **Loading States**: Shows "Analyzing..." while agents work
- **Error Handling**: Graceful error messages if backend is unavailable
- **CORS Support**: Frontend can communicate with backend

### 🎨 Visualization Display
- **PNG Charts**: Display inline in chat bubbles
- **HTML Dashboards**: Button to open in new tab
- **File Management**: Tracks new vs existing visualizations
- **External Links**: Easy access to full dashboard views

## 📁 File Structure

```
Data-agent/
├── agent.py                 # Enhanced with custom FastAPI endpoints
├── start_system.py         # System startup script
├── ui/                     # Next.js frontend
│   ├── components/
│   │   ├── chat-area.tsx   # Enhanced with API integration
│   │   └── message-bubble.tsx # Enhanced with visualization display
│   └── ...
└── output/                 # Generated visualizations served as static files
```

## 🔌 API Endpoints

- `POST /api/chat` - Send messages to agents and get responses with visualizations
- `GET /api/visualizations` - List all available visualizations
- `GET /api/health` - Health check
- `GET /static/{filename}` - Serve generated visualization files

## 🐛 Troubleshooting

### Backend Issues
- Ensure PostgreSQL is running on port 5532
- Check Azure OpenAI credentials in `.env`
- Verify data file exists: `Alpha-NOC-Reports-Jan-to-Apr-2025.xlsx`

### Frontend Issues  
- Run `npm install` in the `ui/` directory
- Check Node.js version (requires Node 16+)
- Ensure port 3000 is available

### Visualization Issues
- Check `output/` directory permissions
- Verify static file mount in FastAPI
- Look for CORS errors in browser console

## 🎯 Usage Tips

1. **Best Questions**: Ask for specific analysis or visualizations
2. **Wait for Loading**: Let agents finish processing before next question  
3. **View Full Dashboards**: Click external link icon for interactive dashboards
4. **Multiple Charts**: Agents can create multiple visualizations per response

## 🔄 System Status

- ✅ Backend API integration
- ✅ Frontend chat interface  
- ✅ Visualization display
- ✅ File serving
- ✅ Real-time updates
- ✅ Error handling
- ✅ Loading states

The system is now fully integrated and ready for use!