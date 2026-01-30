# Perplexity-style Chat UI

A modern, Perplexity AI-inspired chat interface built with Next.js, TypeScript, and Tailwind CSS. Features a light red theme, file attachments, voice recording, model selection, and session management.

## Features

- 🎨 **Modern UI** - Clean, responsive design inspired by Perplexity AI
- 🔴 **Light Red Theme** - Custom color scheme with light red accents
- 💬 **Smart Chat** - Multi-model AI conversations (GPT-4, Claude, Gemini)
- 📎 **File Attachments** - Upload and analyze documents, images, and more
- 🎤 **Voice Recording** - Built-in voice message support
- 🔍 **Search Modes** - Online, local, or combined search capabilities
- 📚 **Session Management** - Persistent chat history with sidebar navigation
- 🔐 **Authentication** - Login/signup pages ready for backend integration
- 🚀 **FastAPI Ready** - Pre-configured for FastAPI backend integration

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd perplexity-chat-ui
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                    # Next.js app router pages
│   ├── auth/              # Authentication pages
│   ├── chat/              # Main chat interface
│   └── page.tsx           # Landing page
├── components/            # Reusable components
│   ├── chat/              # Chat-specific components
│   └── ui/                # Base UI components
├── lib/                   # Utilities and configurations
├── store/                 # Zustand state management
└── types/                 # TypeScript type definitions
```

## Key Components

### Chat Interface
- **Sidebar**: Session management and navigation
- **Message**: Individual message display with attachments
- **ChatInput**: Multi-modal input with file upload and voice recording
- **ModelSelector**: AI model and search mode selection

### Authentication
- **Login/Signup**: Ready-to-use authentication forms
- **Protected Routes**: Session-based access control

### State Management
- **Zustand Store**: Persistent chat sessions and settings
- **Local Storage**: Session and preference persistence

## Backend Integration

This UI is designed to work with a FastAPI backend. See `src/lib/fastapi-integration.md` for detailed integration instructions.

### Required Environment Variables

Create a `.env.local` file:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Endpoints Expected

- `POST /auth/login` - User authentication
- `POST /chat/message` - Send messages
- `POST /chat/upload` - File uploads
- `GET /chat/sessions` - Session management
- `POST /voice/transcribe` - Voice processing

## Customization

### Theme Colors
Edit `tailwind.config.ts` to customize the color scheme:
```typescript
colors: {
  primary: {
    DEFAULT: "#FF6B6B",  // Main red color
    hover: "#FF5252",    // Hover state
    light: "#FFE5E5",    // Light background
  },
  // ... other colors
}
```

### Models and Search Modes
Update `src/components/chat/model-selector.tsx` to add or modify available models and search modes.

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production  
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Technologies Used

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety and better DX
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management
- **Radix UI** - Headless UI components
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Deployment

### Vercel (Recommended)
1. Push to GitHub
2. Connect to Vercel
3. Deploy automatically

### Docker
```bash
# Build the container
docker build -t perplexity-chat-ui .

# Run the container
docker run -p 3000:3000 perplexity-chat-ui
```

## Support

For issues and questions, please open a GitHub issue or contact the development team.
