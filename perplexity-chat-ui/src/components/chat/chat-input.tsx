'use client'

import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { useChatStore } from '@/store/chat-store'
import { 
  SendIcon
} from 'lucide-react'
import { motion } from 'framer-motion'

export default function ChatInput() {
  const [message, setMessage] = useState('')
  const { 
    sendMessage,
    isLoading 
  } = useChatStore()
  
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim()) return
    
    const currentMessage = message
    
    // Clear inputs immediately for better UX
    setMessage('')
    
    // Send message via API
    await sendMessage(currentMessage)
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
      {/* Input Area */}
      <div className="p-4">
        <motion.form
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          onSubmit={handleSubmit}
          className="flex gap-3 items-end"
        >

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

          {/* Send Button */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            animate={
              !message.trim() || isLoading
                ? { opacity: 0.5 }
                : { opacity: 1 }
            }
          >
            <Button
              type="submit"
              disabled={!message.trim() || isLoading}
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
      </div>
    </motion.div>
  )
}