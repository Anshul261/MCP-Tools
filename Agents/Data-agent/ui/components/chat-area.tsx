"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageBubble } from "./message-bubble"
import { Send, Plus, Copy, RotateCcw, Loader2, ImageIcon, Zap } from "lucide-react"
import { Streamdown } from "streamdown"

interface Visualization {
  filename: string
  url: string
  type: "html" | "image"
  created: number
}

interface AnalysisStep {
  type: 'tool_call' | 'agent_switch' | 'progress' | 'visualization'
  title: string
  description: string
  timestamp: string
  agent?: string
  tool?: string
}

interface Message {
  id: number
  content: string
  isUser: boolean
  timestamp: string
  visualizations?: Visualization[]
  agentUsed?: string
  steps?: AnalysisStep[]
}

interface ChatAreaProps {
  selectedChat: string
}

export function ChatArea({ selectedChat }: ChatAreaProps) {
  const [message, setMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>("")
  const [currentSteps, setCurrentSteps] = useState<AnalysisStep[]>([])
  const [currentProgress, setCurrentProgress] = useState<string>("")
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content: `Welcome to the Data Analysis Agent! I can help you analyze your ticket data and create visualizations. Try asking me things like:

• "Show me the monthly ticket trends"
• "Create a chart of ticket categories"
• "What insights can you provide about our support data?"

**Header Buttons:**
Chart Icon - Show recent visualizations
Lightning Icon - Force create pie chart (backup if agents fail)

Start by typing your question below.`,
      isUser: false,
      timestamp: new Date().toLocaleTimeString(),
      agentUsed: "Data Analysis Team"
    },
  ])

  // Initialize session
  useEffect(() => {
    setSessionId(Math.random().toString(36).substring(7))
  }, [])

  const handleShowRecentVisualizations = async () => {
    try {
      const response = await fetch('http://localhost:7777/api/visualizations')
      if (response.ok) {
        const data = await response.json()
        if (data.visualizations && data.visualizations.length > 0) {
          // Get recent visualizations from the last 24 hours
          const oneDayAgo = Date.now() / 1000 - 86400
          const recentViz = data.visualizations.filter((viz: Visualization) =>
            viz.created >= oneDayAgo
          ).slice(0, 8) // Show up to 8 most recent

          const vizMessage: Message = {
            id: Date.now(),
            content: `Here are the most recent visualizations from the last 24 hours (${recentViz.length} found):`,
            isUser: false,
            timestamp: new Date().toLocaleTimeString(),
            visualizations: recentViz,
            agentUsed: "Data Analysis Team"
          }
          setMessages(prev => [...prev, vizMessage])
        } else {
          const noVizMessage: Message = {
            id: Date.now(),
            content: "No recent visualizations found. Try asking me to create a chart or analysis first!",
            isUser: false,
            timestamp: new Date().toLocaleTimeString(),
            agentUsed: "Data Analysis Team"
          }
          setMessages(prev => [...prev, noVizMessage])
        }
      }
    } catch (error) {
      console.error('Error fetching visualizations:', error)
      const errorMessage: Message = {
        id: Date.now(),
        content: "Error fetching visualizations. Please ensure the backend is running.",
        isUser: false,
        timestamp: new Date().toLocaleTimeString(),
        agentUsed: "System Error"
      }
      setMessages(prev => [...prev, errorMessage])
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
    if (!message.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now(),
      content: message,
      isUser: true,
      timestamp: new Date().toLocaleTimeString(),
    }

    setMessages(prev => [...prev, userMessage])
    setMessage("")
    setIsLoading(true)

    try {
      // Create FormData for the AGNO streaming endpoint
      const formData = new FormData()
      formData.append('message', message)
      formData.append('user_id', 'ui-user')
      formData.append('session_id', sessionId)
      formData.append('stream', 'true')
      formData.append('monitor', 'true')

      const response = await fetch("http://localhost:7777/teams/data-analysis-team/runs", {
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
        const initialAiMessage: Message = {
          id: aiMessageId,
          content: "",
          isUser: false,
          timestamp: new Date().toLocaleTimeString(),
          agentUsed: "Data Analysis Team",
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
              } else if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6))

                  if (currentEvent === 'RunContent' && data.content) {
                    accumulatedContent += data.content
                    // Update the message with accumulated content
                    setMessages(prev => prev.map(msg =>
                      msg.id === aiMessageId
                        ? { ...msg, content: accumulatedContent }
                        : msg
                    ))
                  } else if (currentEvent === 'TeamToolCallStarted' || currentEvent === 'ToolCallStarted') {
                    // Add step for tool call started
                    const step: AnalysisStep = {
                      type: 'tool_call',
                      title: `Starting ${data.tool?.tool_name || 'Tool Call'}`,
                      description: data.tool?.tool_args ?
                        `Args: ${JSON.stringify(data.tool.tool_args).substring(0, 100)}...` :
                        'Executing tool...',
                      timestamp: new Date().toLocaleTimeString(),
                      tool: data.tool?.tool_name,
                      agent: data.agent_id || data.team_name
                    }
                    setCurrentSteps(prev => [...prev, step])
                    setCurrentProgress(`Executing ${data.tool?.tool_name || 'tool'}...`)
                  } else if (currentEvent === 'TeamToolCallCompleted' || currentEvent === 'ToolCallCompleted') {
                    // Update step for tool call completed
                    const step: AnalysisStep = {
                      type: 'tool_call',
                      title: `Completed ${data.tool?.tool_name || 'Tool Call'}`,
                      description: `Finished in ${data.tool?.metrics?.duration?.toFixed(2) || 'N/A'}s`,
                      timestamp: new Date().toLocaleTimeString(),
                      tool: data.tool?.tool_name,
                      agent: data.agent_id || data.team_name
                    }
                    setCurrentSteps(prev => [...prev, step])
                  } else if (currentEvent === 'RunStarted') {
                    // Agent switch
                    const step: AnalysisStep = {
                      type: 'agent_switch',
                      title: `Agent Started`,
                      description: `Agent ${data.agent_id || 'Unknown'} is now processing`,
                      timestamp: new Date().toLocaleTimeString(),
                      agent: data.agent_id
                    }
                    setCurrentSteps(prev => [...prev, step])
                    setCurrentProgress(`Agent processing...`)
                  }
                } catch (parseError) {
                  // Ignore parse errors for incomplete chunks
                  console.debug("Parse error:", parseError)
                }
              }
            }
          }

          // When streaming is complete, add steps to the final message and check for visualizations
          setTimeout(async () => {
            const newViz = await find_new_visualizations_after_message()
            setMessages(prev => prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, steps: [...currentSteps], visualizations: newViz }
                : msg
            ))
          }, 2000)

          // Additional fallback: if response mentions creating visualizations, force check
          if (accumulatedContent.toLowerCase().includes('created') ||
              accumulatedContent.toLowerCase().includes('saved') ||
              accumulatedContent.toLowerCase().includes('chart') ||
              accumulatedContent.toLowerCase().includes('visualization') ||
              accumulatedContent.toLowerCase().includes('.png')) {
            setTimeout(async () => {
              const additionalViz = await find_new_visualizations_after_message()
              if (additionalViz.length > 0) {
                setMessages(prev => prev.map(msg =>
                  msg.id === aiMessageId
                    ? { ...msg, visualizations: additionalViz }
                    : msg
                ))
              }
            }, 4000)
          }
        } finally {
          reader.releaseLock()
          setCurrentSteps([])
          setCurrentProgress("")
        }
      } else {
        // Fallback for non-streaming response
        const data = await response.json()
        const aiMessageId = Date.now() + 1
        const aiMessage: Message = {
          id: aiMessageId,
          content: data.content || data.message || "No response received",
          isUser: false,
          timestamp: new Date().toLocaleTimeString(),
          agentUsed: "Data Analysis Team",
        }
        setMessages(prev => [...prev, aiMessage])

        // Also check for visualizations in non-streaming mode
        setTimeout(async () => {
          const newViz = await find_new_visualizations_after_message()
          if (newViz.length > 0) {
            setMessages(prev => prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, visualizations: newViz }
                : msg
            ))
          }
        }, 2000)
      }
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: Message = {
        id: Date.now() + 1,
        content: "Sorry, I'm having trouble connecting to the Data Analysis Team. Please make sure the AgentOS server is running on port 7777.",
        isUser: false,
        timestamp: new Date().toLocaleTimeString(),
        agentUsed: "System Error"
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const find_new_visualizations_after_message = async (): Promise<Visualization[]> => {
    try {
      const response = await fetch('http://localhost:7777/api/visualizations')
      if (response.ok) {
        const data = await response.json()
        // Get visualizations from the last 5 minutes (300 seconds)
        const fiveMinutesAgo = Date.now() / 1000 - 300
        const recentViz = data.visualizations?.filter((viz: Visualization) =>
          viz.created >= fiveMinutesAgo
        ).slice(0, 5) || []
        console.log('Found recent visualizations:', recentViz)
        return recentViz
      }
    } catch (error) {
      console.error('Error fetching visualizations:', error)
    }
    return []
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
            agentUsed={msg.agentUsed}
            steps={msg.steps}
          />
        ))}
        {isLoading && (
          <div className="flex items-center space-x-2 text-muted-foreground">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-accent"></div>
            <span>{currentProgress || "Analyzing..."}</span>
          </div>
        )}
        {currentSteps.length > 0 && isLoading && (
          <div className="text-xs text-muted-foreground space-y-1">
            {currentSteps.slice(-3).map((step, index) => (
              <div key={index} className="flex items-center gap-2">
                <div className="w-1 h-1 rounded-full bg-accent" />
                <span>{step.title}</span>
                {step.agent && <span className="text-accent">({step.agent})</span>}
              </div>
            ))}
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
