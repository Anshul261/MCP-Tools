'use client'

import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { useChatStore } from '@/store/chat-store'
import { FileAttachment } from '@/types'
import { generateId } from '@/lib/utils'
import { 
  SendIcon, 
  PaperclipIcon, 
  MicIcon, 
  MicOffIcon,
  XIcon,
  FileIcon
} from 'lucide-react'

export default function ChatInput() {
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState<FileAttachment[]>([])
  const [files, setFiles] = useState<File[]>([])
  const { 
    sendMessage,
    isLoading, 
    isRecording,
    setRecording 
  } = useChatStore()
  
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim() && files.length === 0) return
    
    const currentMessage = message
    const currentFiles = files
    
    // Clear inputs immediately for better UX
    setMessage('')
    setAttachments([])
    setFiles([])
    
    // Send message via API
    await sendMessage(currentMessage, currentFiles.length > 0 ? currentFiles : undefined)
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    
    // Store both the actual files and the attachment metadata
    setFiles(prev => [...prev, ...selectedFiles])
    
    const newAttachments: FileAttachment[] = selectedFiles.map(file => ({
      id: generateId(),
      name: file.name,
      size: file.size,
      type: file.type,
      url: URL.createObjectURL(file)
    }))
    
    setAttachments(prev => [...prev, ...newAttachments])
  }

  const removeAttachment = (attachmentId: string) => {
    // Find the attachment to remove
    const attachmentToRemove = attachments.find(a => a.id === attachmentId)
    if (attachmentToRemove) {
      // Remove from files array as well
      setFiles(prev => prev.filter(f => f.name !== attachmentToRemove.name))
    }
    setAttachments(prev => prev.filter(a => a.id !== attachmentId))
  }

  const handleVoiceToggle = () => {
    if (isRecording) {
      // Stop recording
      setRecording(false)
      setMessage(prev => prev + ' [Voice message ended]')
    } else {
      // Start recording
      setRecording(true)
      setMessage(prev => prev + ' [Voice message started]')
    }
  }

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
    }
  }

  return (
    <div className="border-t border-border bg-background">
      {/* File Attachments Preview */}
      {attachments.length > 0 && (
        <div className="p-4 border-b border-border">
          <div className="flex flex-wrap gap-2">
            {attachments.map((attachment) => (
              <div
                key={attachment.id}
                className="flex items-center gap-2 bg-accent rounded-lg p-2"
              >
                <FileIcon className="h-4 w-4 text-primary" />
                <span className="text-sm text-foreground truncate max-w-32">
                  {attachment.name}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeAttachment(attachment.id)}
                  className="h-6 w-6"
                >
                  <XIcon className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4">
        <form onSubmit={handleSubmit} className="flex gap-3 items-end">
          {/* File Upload */}
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            className="shrink-0"
          >
            <PaperclipIcon className="h-5 w-5" />
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileUpload}
            className="hidden"
            accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
          />

          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => {
                setMessage(e.target.value)
                adjustTextareaHeight()
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
              placeholder="Ask anything..."
              className="w-full resize-none rounded-lg border border-border bg-input px-4 py-3 text-foreground placeholder-foreground-muted focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              rows={1}
              disabled={isLoading}
            />
          </div>

          {/* Voice Recording */}
          <Button
            type="button"
            variant={isRecording ? "destructive" : "ghost"}
            size="icon"
            onClick={handleVoiceToggle}
            className="shrink-0"
          >
            {isRecording ? (
              <MicOffIcon className="h-5 w-5" />
            ) : (
              <MicIcon className="h-5 w-5" />
            )}
          </Button>

          {/* Send Button */}
          <Button
            type="submit"
            disabled={(!message.trim() && attachments.length === 0) || isLoading}
            className="shrink-0"
          >
            <SendIcon className="h-5 w-5" />
          </Button>
        </form>

        {/* Recording Indicator */}
        {isRecording && (
          <div className="flex items-center gap-2 mt-2 text-destructive">
            <div className="w-2 h-2 bg-destructive rounded-full animate-pulse" />
            <span className="text-sm">Recording voice message...</span>
          </div>
        )}
      </div>
    </div>
  )
}