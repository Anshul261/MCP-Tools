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
import { motion, AnimatePresence } from 'framer-motion'

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
    <motion.div
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="border-t border-border/50 bg-gradient-to-r from-background via-background-secondary to-background backdrop-blur-sm"
    >
      {/* File Attachments Preview */}
      <AnimatePresence>
        {attachments.length > 0 && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden border-b border-border/30"
          >
            <div className="p-4">
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
                className="flex flex-wrap gap-2"
              >
                {attachments.map((attachment, index) => (
                  <motion.div
                    key={attachment.id}
                    initial={{ opacity: 0, scale: 0.8, x: -20 }}
                    animate={{ opacity: 1, scale: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.8, x: 20 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                    whileHover={{ scale: 1.05, y: -2 }}
                    className="flex items-center gap-2 bg-gradient-to-r from-accent/50 to-accent/30 backdrop-blur-sm rounded-lg p-2 border border-border/30 shadow-sm"
                  >
                    <motion.div
                      animate={{ rotate: [0, 10, -10, 0] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <FileIcon className="h-4 w-4 text-primary" />
                    </motion.div>
                    <span className="text-sm text-foreground truncate max-w-32">
                      {attachment.name}
                    </span>
                    <motion.div whileHover={{ scale: 1.2 }} whileTap={{ scale: 0.8 }}>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeAttachment(attachment.id)}
                        className="h-6 w-6 hover:bg-destructive/20 hover:text-destructive transition-colors duration-200"
                      >
                        <XIcon className="h-3 w-3" />
                      </Button>
                    </motion.div>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input Area */}
      <div className="p-4">
        <motion.form
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          onSubmit={handleSubmit}
          className="flex gap-3 items-end"
        >
          {/* File Upload */}
          <motion.div
            whileHover={{ scale: 1.1, rotate: 5 }}
            whileTap={{ scale: 0.9 }}
          >
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              className="shrink-0 hover:bg-gradient-to-r hover:from-accent/50 hover:to-accent/30 transition-all duration-200"
            >
              <PaperclipIcon className="h-5 w-5" />
            </Button>
          </motion.div>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileUpload}
            className="hidden"
            accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
          />

          {/* Text Input */}
          <motion.div
            className="flex-1 relative"
            whileFocus={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <motion.textarea
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
              className="w-full resize-none rounded-xl border border-border/50 bg-input/50 backdrop-blur-sm px-4 py-3 text-foreground placeholder-foreground-muted focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-300 shadow-sm hover:shadow-md"
              rows={1}
              disabled={isLoading}
              whileFocus={{ borderColor: "#FF6B6B" }}
            />
            
            {/* Animated border effect */}
            {message && (
              <motion.div
                className="absolute inset-0 rounded-xl border-2 border-primary/30 pointer-events-none"
                initial={{ opacity: 0, scale: 1.05 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.05 }}
                transition={{ duration: 0.2 }}
              />
            )}
          </motion.div>

          {/* Voice Recording */}
          <motion.div
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            animate={isRecording ? { scale: [1, 1.1, 1] } : { scale: 1 }}
            transition={isRecording ? { duration: 1, repeat: Infinity, ease: "easeInOut" } : { duration: 0.2 }}
          >
            <Button
              type="button"
              variant={isRecording ? "destructive" : "ghost"}
              size="icon"
              onClick={handleVoiceToggle}
              className={`shrink-0 transition-all duration-300 ${
                isRecording 
                  ? 'shadow-lg shadow-destructive/25 hover:shadow-destructive/40' 
                  : 'hover:bg-gradient-to-r hover:from-accent/50 hover:to-accent/30'
              }`}
            >
              <motion.div
                animate={{ rotate: isRecording ? 360 : 0 }}
                transition={{ duration: isRecording ? 2 : 0.3, repeat: isRecording ? Infinity : 0, ease: "linear" }}
              >
                {isRecording ? (
                  <MicOffIcon className="h-5 w-5" />
                ) : (
                  <MicIcon className="h-5 w-5" />
                )}
              </motion.div>
            </Button>
          </motion.div>

          {/* Send Button */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            animate={
              (!message.trim() && attachments.length === 0) || isLoading
                ? { opacity: 0.5 }
                : { opacity: 1 }
            }
          >
            <Button
              type="submit"
              disabled={(!message.trim() && attachments.length === 0) || isLoading}
              className="shrink-0 bg-gradient-to-r from-primary to-primary-hover hover:from-primary-hover hover:to-primary shadow-lg hover:shadow-primary/25 transition-all duration-300 relative overflow-hidden"
            >
              {isLoading && (
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
              )}
              <motion.div
                animate={{ rotate: isLoading ? 360 : 0 }}
                transition={{ duration: isLoading ? 1 : 0.3, repeat: isLoading ? Infinity : 0, ease: "linear" }}
                className="relative z-10"
              >
                <SendIcon className="h-5 w-5" />
              </motion.div>
            </Button>
          </motion.div>
        </motion.form>

        {/* Recording Indicator */}
        <AnimatePresence>
          {isRecording && (
            <motion.div
              initial={{ opacity: 0, y: 10, height: 0 }}
              animate={{ opacity: 1, y: 0, height: "auto" }}
              exit={{ opacity: 0, y: -10, height: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="flex items-center gap-2 mt-3 text-destructive overflow-hidden"
            >
              <motion.div
                className="w-3 h-3 bg-destructive rounded-full"
                animate={{ 
                  scale: [1, 1.5, 1],
                  opacity: [1, 0.5, 1]
                }}
                transition={{ 
                  duration: 1, 
                  repeat: Infinity, 
                  ease: "easeInOut" 
                }}
              />
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-sm font-medium"
              >
                Recording voice message...
              </motion.span>
              <motion.div
                className="flex gap-1 ml-2"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-1 h-4 bg-destructive/60 rounded-full"
                    animate={{ 
                      scaleY: [0.5, 1, 0.5],
                      opacity: [0.5, 1, 0.5]
                    }}
                    transition={{ 
                      duration: 1, 
                      repeat: Infinity, 
                      delay: i * 0.1,
                      ease: "easeInOut" 
                    }}
                  />
                ))}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}