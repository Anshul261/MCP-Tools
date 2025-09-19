"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageBubble } from "./message-bubble"
import { Send, Plus, Copy, RotateCcw } from "lucide-react"

interface ChatAreaProps {
  selectedChat: string
}

interface ChatMessage {
  id: number
  content: string
  isUser: boolean
  timestamp: string
  agentUsed?: string
}

export function ChatArea({ selectedChat }: ChatAreaProps) {
  const [message, setMessage] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>("")

  // Initialize session
  useEffect(() => {
    setSessionId(Math.random().toString(36).substring(7))
    // Set initial message for stock analysis
    if (selectedChat === "Stock Analysis") {
      setMessages([{
        id: 1,
        content: "Welcome to Stock Analysis! I'm your AI-powered stock analysis team. Ask me about any stock ticker (e.g., 'Analyze AAPL', 'What's the outlook for TSLA?', 'Should I invest in NVDA?')",
        isUser: false,
        timestamp: new Date().toLocaleTimeString(),
        agentUsed: "Stock Analysis Team"
      }])
    } else {
      setMessages([{
        id: 1,
        content: `Welcome to ${selectedChat}! Start a conversation by typing a message below.`,
        isUser: false,
        timestamp: new Date().toLocaleTimeString(),
      }])
    }
  }, [selectedChat])

  const sendMessage = async () => {
    if (!message.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now(),
      content: message,
      isUser: true,
      timestamp: new Date().toLocaleTimeString(),
    }

    setMessages(prev => [...prev, userMessage])
    setMessage("")
    setIsLoading(true)

    try {
      // Create FormData for multipart/form-data request
      const formData = new FormData()
      formData.append('message', message)
      formData.append('user_id', 'ui-user')
      formData.append('session_id', sessionId)
      formData.append('stream', 'true')
      formData.append('monitor', 'true')

      const response = await fetch("http://localhost:7777/teams/fast-stock-analysis-team/runs", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Handle streaming response
      if (response.body) {
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let accumulatedContent = ""
        let buffer = ""

        // Add initial AI message that will be updated with streaming content
        const aiMessageId = Date.now() + 1
        const initialAiMessage: ChatMessage = {
          id: aiMessageId,
          content: "",
          isUser: false,
          timestamp: new Date().toLocaleTimeString(),
          agentUsed: "Stock Analysis Team",
        }
        setMessages(prev => [...prev, initialAiMessage])

        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value, { stream: true })
            buffer += chunk

            // Process complete lines from buffer
            const lines = buffer.split('\n')
            buffer = lines.pop() || "" // Keep incomplete line in buffer

            let currentEvent = ""
            for (const line of lines) {
              if (line.startsWith('event: ')) {
                currentEvent = line.slice(7).trim()
              } else if (line.startsWith('data: ') && currentEvent === 'RunContent') {
                try {
                  const data = JSON.parse(line.slice(6))
                  if (data.content) {
                    accumulatedContent += data.content
                    // Update the message with accumulated content
                    setMessages(prev => prev.map(msg =>
                      msg.id === aiMessageId
                        ? { ...msg, content: accumulatedContent }
                        : msg
                    ))
                  }
                } catch (parseError) {
                  // Ignore parse errors for incomplete chunks
                  console.debug("Parse error:", parseError)
                }
              }
            }
          }
        } finally {
          reader.releaseLock()
        }
      } else {
        // Fallback for non-streaming response
        const data = await response.json()
        const aiMessage: ChatMessage = {
          id: Date.now() + 1,
          content: data.content || data.message || "No response received",
          isUser: false,
          timestamp: new Date().toLocaleTimeString(),
          agentUsed: "Stock Analysis Team",
        }
        setMessages(prev => [...prev, aiMessage])
      }
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        content: "Sorry, I'm having trouble connecting to the analysis system. Please make sure the AgentOS server is running on port 7777.",
        isUser: false,
        timestamp: new Date().toLocaleTimeString(),
        agentUsed: "System Error"
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSend = () => {
    sendMessage()
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Chat Header */}
      <div className="p-4 border-b border-border glass-strong bg-card/30">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">{selectedChat}</h2>
          <div className="flex items-center gap-2">
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
          <MessageBubble key={msg.id} content={msg.content} isUser={msg.isUser} timestamp={msg.timestamp} />
        ))}
        {isLoading && (
          <div className="flex items-center space-x-2 text-muted-foreground">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-accent"></div>
            <span>Analyzing...</span>
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
              placeholder={selectedChat === "Stock Analysis" ? "Ask about stocks (e.g., 'Analyze AAPL')..." : "Type a message..."}
              className="glass bg-input/50 border-border text-foreground placeholder:text-muted-foreground pr-12"
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
              disabled={isLoading}
            />
            <Button
              onClick={handleSend}
              size="sm"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-accent hover:bg-accent/80 text-accent-foreground"
              disabled={isLoading || !message.trim()}
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
