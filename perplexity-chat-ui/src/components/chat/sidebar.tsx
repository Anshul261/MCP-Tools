'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useChatStore } from '@/store/chat-store'
import { Session } from '@/types'
import { formatDate } from '@/lib/utils'
import { PlusIcon, MessageSquareIcon, SettingsIcon, TrashIcon } from 'lucide-react'

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { 
    sessions, 
    currentSession, 
    createSession, 
    setCurrentSession, 
    deleteSession 
  } = useChatStore()

  const handleNewChat = () => {
    createSession()
  }

  const handleSessionClick = (session: Session) => {
    setCurrentSession(session)
  }

  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation()
    deleteSession(sessionId)
  }

  if (isCollapsed) {
    return (
      <div className="w-16 bg-background-secondary border-r border-border flex flex-col items-center py-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(false)}
          className="mb-4"
        >
          <MessageSquareIcon className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={handleNewChat}
          className="mb-4"
        >
          <PlusIcon className="h-5 w-5" />
        </Button>
      </div>
    )
  }

  return (
    <div className="w-80 bg-background-secondary border-r border-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-foreground">Chats</h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsCollapsed(true)}
          >
            <MessageSquareIcon className="h-5 w-5" />
          </Button>
        </div>
        <Button
          onClick={handleNewChat}
          className="w-full bg-primary hover:bg-primary-hover"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          New Chat
        </Button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.length === 0 ? (
          <div className="text-center py-8 text-foreground-muted">
            <MessageSquareIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No conversations yet</p>
            <p className="text-sm">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => handleSessionClick(session)}
                className={`
                  group relative p-3 rounded-lg cursor-pointer transition-colors
                  ${currentSession?.id === session.id 
                    ? 'bg-primary/10 border border-primary/20' 
                    : 'hover:bg-accent hover:bg-opacity-50'
                  }
                `}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-foreground truncate">
                      {session.title}
                    </h3>
                    <p className="text-sm text-foreground-secondary mt-1">
                      {session.updatedAt ? formatDate(session.updatedAt) : 'Recent'}
                    </p>
                    <p className="text-xs text-foreground-muted mt-1">
                      {session.messages.length} messages
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => handleDeleteSession(e, session.id)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <Button
          variant="ghost"
          className="w-full justify-start"
        >
          <SettingsIcon className="h-4 w-4 mr-2" />
          Settings
        </Button>
      </div>
    </div>
  )
}