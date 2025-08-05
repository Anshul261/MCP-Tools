'use client'

import { Message as MessageType } from '@/types'
import { formatDate, cn } from '@/lib/utils'
import { UserIcon, BotIcon, VolumeXIcon } from 'lucide-react'

interface MessageProps {
  message: MessageType
}

export default function Message({ message }: MessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn(
      "flex gap-4 p-6 border-b border-border/50",
      isUser ? "bg-background" : "bg-background-secondary/30"
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser 
          ? "bg-primary text-white" 
          : "bg-accent text-foreground"
      )}>
        {isUser ? (
          <UserIcon className="h-4 w-4" />
        ) : (
          <BotIcon className="h-4 w-4" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <span className="font-medium text-foreground">
            {isUser ? 'You' : 'Assistant'}
          </span>
          {message.isVoice && (
            <VolumeXIcon className="h-4 w-4 text-primary" />
          )}
          <span className="text-xs text-foreground-muted">
            {message.timestamp ? formatDate(message.timestamp) : 'Now'}
          </span>
        </div>

        {/* Message Content */}
        <div className="prose prose-sm max-w-none text-foreground">
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* File Attachments */}
        {message.files && message.files.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.files.map((file) => (
              <div
                key={file.id}
                className="flex items-center gap-2 p-2 bg-accent rounded-lg"
              >
                <div className="w-8 h-8 bg-primary/20 rounded flex items-center justify-center">
                  <span className="text-xs font-medium text-primary">
                    {file.name.split('.').pop()?.toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-foreground-muted">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}