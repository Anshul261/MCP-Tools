'use client'

import { useEffect } from 'react'
import { useChatStore } from '@/store/chat-store'
import Sidebar from '@/components/chat/sidebar'
import Message from '@/components/chat/message'
import ChatInput from '@/components/chat/chat-input'
import ModelSelector from '@/components/chat/model-selector'
import { Button } from '@/components/ui/button'
import { SparklesIcon, MessageSquareIcon } from 'lucide-react'

export default function ChatPage() {
  const { currentSession, createSession, isLoading } = useChatStore()

  // Create initial session if none exists
  useEffect(() => {
    if (!currentSession) {
      createSession()
    }
  }, [currentSession, createSession])

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-border bg-background-secondary px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <SparklesIcon className="h-6 w-6 text-primary" />
                <h1 className="text-xl font-semibold text-foreground">
                  AI Chat Assistant
                </h1>
              </div>
            </div>
            <div className="w-64">
              <ModelSelector />
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {!currentSession || currentSession.messages.length === 0 ? (
            <div className="flex-1 flex items-center justify-center p-8">
              <div className="text-center max-w-md">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MessageSquareIcon className="h-8 w-8 text-primary" />
                </div>
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Start a conversation
                </h2>
                <p className="text-foreground-secondary mb-6">
                  Ask me anything! I can search the web, analyze documents, and help with various tasks.
                </p>
                <div className="grid gap-2">
                  <Button
                    variant="outline"
                    className="justify-start h-auto p-4 text-left"
                    onClick={() => {
                      // Add example message
                    }}
                  >
                    <div>
                      <div className="font-medium">What&apos;s the latest news in AI?</div>
                      <div className="text-sm text-foreground-muted">Search for recent AI developments</div>
                    </div>
                  </Button>
                  <Button
                    variant="outline"
                    className="justify-start h-auto p-4 text-left"
                    onClick={() => {
                      // Add example message
                    }}
                  >
                    <div>
                      <div className="font-medium">Analyze this document</div>
                      <div className="text-sm text-foreground-muted">Upload and analyze files</div>
                    </div>
                  </Button>
                  <Button
                    variant="outline"
                    className="justify-start h-auto p-4 text-left"
                    onClick={() => {
                      // Add example message
                    }}
                  >
                    <div>
                      <div className="font-medium">Help me write code</div>
                      <div className="text-sm text-foreground-muted">Get coding assistance</div>
                    </div>
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div>
              {currentSession.messages.map((message) => (
                <Message key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex gap-4 p-6 border-b border-border/50 bg-background-secondary/30">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent flex items-center justify-center">
                    <SparklesIcon className="h-4 w-4 animate-pulse" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium text-foreground">Assistant</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <ChatInput />
      </div>
    </div>
  )
}