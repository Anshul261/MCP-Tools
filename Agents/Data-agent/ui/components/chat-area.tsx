"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageBubble } from "./message-bubble"
import { Send, Plus, Copy, RotateCcw, Loader2, ImageIcon, Zap } from "lucide-react"

interface Visualization {
  filename: string
  url: string
  type: "html" | "image"
  created: number
}

interface Message {
  id: number
  content: string
  isUser: boolean
  timestamp: string
  visualizations?: Visualization[]
}

interface ChatAreaProps {
  selectedChat: string
}

export function ChatArea({ selectedChat }: ChatAreaProps) {
  const [message, setMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content: `Welcome to the Data Analysis Agent! I can help you analyze your ticket data and create visualizations. Try asking me things like:

• "Show me the monthly ticket trends"
• "Create a chart of ticket categories"  
• "What insights can you provide about our support data?"

**Header Buttons:**
📊 - Show recent visualizations
⚡ - Force create pie chart (backup if agents fail)

Start by typing your question below.`,
      isUser: false,
      timestamp: new Date().toLocaleTimeString(),
    },
  ])

  const handleShowRecentVisualizations = async () => {
    try {
      const response = await fetch('http://localhost:7777/api/visualizations')
      if (response.ok) {
        const data = await response.json()
        if (data.visualizations && data.visualizations.length > 0) {
          const vizMessage: Message = {
            id: messages.length + 1,
            content: "Here are the most recent visualizations available:",
            isUser: false,
            timestamp: new Date().toLocaleTimeString(),
            visualizations: data.visualizations.slice(0, 5), // Show up to 5 most recent
          }
          setMessages(prev => [...prev, vizMessage])
        } else {
          const noVizMessage: Message = {
            id: messages.length + 1,
            content: "No visualizations found. Try asking me to create a chart or analysis first!",
            isUser: false,
            timestamp: new Date().toLocaleTimeString(),
          }
          setMessages(prev => [...prev, noVizMessage])
        }
      }
    } catch (error) {
      console.error('Error fetching visualizations:', error)
    }
  }

  const handleForceVisualization = async () => {
    try {
      const response = await fetch('http://localhost:7777/api/force-visualization', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'pie', query: 'SELECT Category, COUNT(*) as count FROM data GROUP BY Category' })
      })
      
      if (response.ok) {
        // Wait a moment then fetch latest visualizations
        setTimeout(async () => {
          const vizResponse = await fetch('http://localhost:7777/api/visualizations')
          if (vizResponse.ok) {
            const data = await vizResponse.json()
            const vizMessage: Message = {
              id: messages.length + 1,
              content: "I've force-created a pie chart visualization for you:",
              isUser: false,
              timestamp: new Date().toLocaleTimeString(),
              visualizations: data.visualizations.slice(0, 1), // Show the newest one
            }
            setMessages(prev => [...prev, vizMessage])
          }
        }, 2000)
      }
    } catch (error) {
      console.error('Error forcing visualization:', error)
    }
  }

  const handleSend = async () => {
    if (message.trim() && !isLoading) {
      const userMessage: Message = {
        id: messages.length + 1,
        content: message.trim(),
        isUser: true,
        timestamp: new Date().toLocaleTimeString(),
      }
      
      setMessages(prev => [...prev, userMessage])
      setMessage("")
      setIsLoading(true)
      
      try {
        const response = await fetch('http://localhost:7777/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: message.trim(),
            chat_id: selectedChat,
          }),
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        
        const aiMessage: Message = {
          id: messages.length + 2,
          content: data.response,
          isUser: false,
          timestamp: new Date().toLocaleTimeString(),
          visualizations: data.visualizations || [],
        }
        
        setMessages(prev => [...prev, aiMessage])
        
      } catch (error) {
        console.error('Error sending message:', error)
        const errorMessage: Message = {
          id: messages.length + 2,
          content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please make sure the data agent backend is running on port 7777.`,
          isUser: false,
          timestamp: new Date().toLocaleTimeString(),
        }
        setMessages(prev => [...prev, errorMessage])
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Chat Header */}
      <div className="p-4 border-b border-border glass-strong bg-card/30">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">{selectedChat}</h2>
          <div className="flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-muted-foreground hover:text-foreground"
              onClick={handleShowRecentVisualizations}
              title="Show recent visualizations"
            >
              <ImageIcon className="w-4 h-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-muted-foreground hover:text-foreground"
              onClick={handleForceVisualization}
              title="Force create pie chart (if agents fail)"
            >
              <Zap className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
              <Copy className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
              <RotateCcw className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <MessageBubble 
            key={msg.id} 
            content={msg.content} 
            isUser={msg.isUser} 
            timestamp={msg.timestamp}
            visualizations={msg.visualizations}
          />
        ))}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 flex-shrink-0 mt-1 rounded-full bg-accent flex items-center justify-center">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
            <div className="max-w-[70%] space-y-2">
              <div className="p-4 rounded-2xl glass border bg-card/60 text-card-foreground border-border shadow-border/10">
                <p className="text-sm leading-relaxed text-muted-foreground">
                  Analyzing data and generating visualizations...
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Message Input */}
      <div className="p-4 border-t border-border glass-strong bg-card/30">
        <div className="flex items-end gap-3">
          <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground mb-2">
            <Plus className="w-5 h-5" />
          </Button>

          <div className="flex-1 relative">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type a message..."
              className="glass bg-input/50 border-border text-foreground placeholder:text-muted-foreground pr-12"
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
            />
            <Button
              onClick={handleSend}
              size="sm"
              disabled={isLoading || !message.trim()}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-accent hover:bg-accent/80 text-accent-foreground disabled:opacity-50"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
