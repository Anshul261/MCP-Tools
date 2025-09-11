"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageBubble } from "./message-bubble"
import { Send, Plus, Copy, RotateCcw } from "lucide-react"

interface ChatAreaProps {
  selectedChat: string
}

export function ChatArea({ selectedChat }: ChatAreaProps) {
  const [message, setMessage] = useState("")

  const messages = {
    "Startup Pitch": [
      {
        id: 1,
        content: "One dominates enterprise clients, another focuses on SMBs, and the last competes with lower pricing.",
        isUser: false,
        timestamp: "2:30 PM",
      },
      {
        id: 2,
        content:
          "They generally lack the balance between ease of use and powerful features. Your product could stand out by being both user-friendly and feature-rich.",
        isUser: false,
        timestamp: "2:32 PM",
      },
      {
        id: 3,
        content:
          "Emphasize your simplicity, clear onboarding, and intuitive design. These are areas where the competition struggles.",
        isUser: false,
        timestamp: "2:35 PM",
      },
      {
        id: 4,
        content:
          '"Novaa helps teams move faster with intuitive project management that actually works for growing businesses."',
        isUser: false,
        timestamp: "2:38 PM",
      },
    ],
    "Marketing Plan": [
      {
        id: 1,
        content: "Let's create a comprehensive marketing strategy for Q4. What are our main objectives?",
        isUser: true,
        timestamp: "10:15 AM",
      },
      {
        id: 2,
        content:
          "Based on your previous campaigns, I'd recommend focusing on three key areas: content marketing, social media engagement, and email automation.",
        isUser: false,
        timestamp: "10:16 AM",
      },
    ],
    "Competitor Analysis": [
      {
        id: 1,
        content: "I need help analyzing our main competitors. Can you break down their strengths and weaknesses?",
        isUser: true,
        timestamp: "9:30 AM",
      },
      {
        id: 2,
        content:
          "I'll analyze the top 3 competitors in your space. Let me start with their market positioning and pricing strategies.",
        isUser: false,
        timestamp: "9:31 AM",
      },
    ],
    "Q2 Strategy": [
      {
        id: 1,
        content: "What should our focus be for Q2 growth initiatives?",
        isUser: true,
        timestamp: "11:00 AM",
      },
      {
        id: 2,
        content:
          "For Q2, I recommend focusing on customer retention, expanding into new market segments, and optimizing your conversion funnel.",
        isUser: false,
        timestamp: "11:02 AM",
      },
    ],
    "Daily Journal": [
      {
        id: 1,
        content: "Today was productive! Finished the design mockups and got great feedback from the team.",
        isUser: true,
        timestamp: "8:45 PM",
      },
      {
        id: 2,
        content:
          "That's wonderful! It sounds like you're making great progress. What aspect of the feedback was most valuable?",
        isUser: false,
        timestamp: "8:46 PM",
      },
    ],
    "Coding Help": [
      {
        id: 1,
        content: "I'm struggling with implementing a responsive navigation menu. Any suggestions?",
        isUser: true,
        timestamp: "3:15 PM",
      },
      {
        id: 2,
        content:
          "I can help you with that! Let's start with a mobile-first approach using flexbox. Here's a clean solution...",
        isUser: false,
        timestamp: "3:16 PM",
      },
    ],
    "Travel Itinerary": [
      {
        id: 1,
        content: "Planning a trip to Japan next month. Need help with the itinerary!",
        isUser: true,
        timestamp: "1:20 PM",
      },
    ],
    "Book Summary": [
      {
        id: 1,
        content: "Can you help me summarize the key points from 'Atomic Habits'?",
        isUser: true,
        timestamp: "7:30 PM",
      },
    ],
    "Grocery List": [
      {
        id: 1,
        content: "Need to plan meals for the week. What should I add to my grocery list?",
        isUser: true,
        timestamp: "12:00 PM",
      },
    ],
  }

  const currentMessages = messages[selectedChat as keyof typeof messages] || [
    {
      id: 1,
      content: `Welcome to ${selectedChat}! Start a conversation by typing a message below.`,
      isUser: false,
      timestamp: "Now",
    },
  ]

  const handleSend = () => {
    if (message.trim()) {
      // Handle sending message
      setMessage("")
    }
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
        {currentMessages.map((msg) => (
          <MessageBubble key={msg.id} content={msg.content} isUser={msg.isUser} timestamp={msg.timestamp} />
        ))}
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
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-accent hover:bg-accent/80 text-accent-foreground"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
