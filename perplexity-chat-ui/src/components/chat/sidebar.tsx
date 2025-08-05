'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useChatStore } from '@/store/chat-store'
import { Session } from '@/types'
import { formatDate } from '@/lib/utils'
import { PlusIcon, MessageSquareIcon, SettingsIcon, TrashIcon, ChevronLeftIcon, ChevronRightIcon, SparklesIcon, TrendingUpIcon, ClockIcon, LogOutIcon } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const router = useRouter()
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

  const handleLogout = async () => {
    // Clear any stored auth tokens
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
    
    // Navigate to login page
    router.push('/auth/login')
  }

  return (
    <motion.div
      initial={{ width: 320 }}
      animate={{ width: isCollapsed ? 64 : 320 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="bg-gradient-to-b from-background-secondary via-background to-background-secondary border-r border-border flex flex-col overflow-hidden relative"
    >
      {/* Animated Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <motion.div
          className="absolute top-10 left-4 w-32 h-32 bg-primary rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-20 right-4 w-24 h-24 bg-primary-hover rounded-full blur-2xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.15, 0.05, 0.15],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2
          }}
        />
      </div>
      {/* Collapse/Expand Button - Positioned on the right edge */}
      <div className="absolute top-4 right-2 z-20">
        <motion.button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded-lg bg-background-secondary/80 backdrop-blur-sm border border-border/50 hover:bg-accent transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <motion.div
            animate={{ rotate: isCollapsed ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronLeftIcon className="h-4 w-4 text-foreground" />
          </motion.div>
        </motion.button>
      </div>

      <AnimatePresence mode="wait">
        {isCollapsed ? (
          <motion.div
            key="collapsed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2, delay: 0.1 }}
            className="flex flex-col items-center py-4 mt-16"
          >
            <motion.div
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <Button
                variant="ghost"
                size="icon"
                onClick={handleNewChat}
                className="mb-4 bg-gradient-to-r from-primary/20 to-primary/10 hover:from-primary/30 hover:to-primary/20 border border-primary/20"
              >
                <PlusIcon className="h-5 w-5 text-primary" />
              </Button>
            </motion.div>
          </motion.div>
        ) : (
          <motion.div
            key="expanded"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2, delay: 0.1 }}
            className="flex flex-col h-full"
          >
            {/* Header */}
            <div className="p-4 pt-16 border-b border-border/50 relative z-10">
              <motion.div
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-foreground bg-gradient-to-r from-foreground to-foreground-secondary bg-clip-text text-transparent">
                    Chats
                  </h2>
                  <motion.div
                    animate={{ 
                      rotate: 360,
                      scale: [1, 1.1, 1]
                    }}
                    transition={{ 
                      rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                      scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
                    }}
                  >
                    <SparklesIcon className="h-4 w-4 text-primary/60" />
                  </motion.div>
                </div>

                {/* Stats */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.3 }}
                  className="flex items-center gap-4 mb-4 text-xs text-foreground-muted"
                >
                  <div className="flex items-center gap-1">
                    <TrendingUpIcon className="h-3 w-3" />
                    <span>{sessions.length} chats</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <ClockIcon className="h-3 w-3" />
                    <span>Recent</span>
                  </div>
                </motion.div>

                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Button
                    onClick={handleNewChat}
                    className="w-full bg-gradient-to-r from-primary to-primary-hover hover:from-primary-hover hover:to-primary shadow-lg hover:shadow-primary/25 transition-all duration-200 relative overflow-hidden"
                  >
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                      animate={{ x: ['-100%', '100%'] }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    />
                    <motion.div
                      whileHover={{ rotate: 90 }}
                      transition={{ duration: 0.2 }}
                      className="relative z-10"
                    >
                      <PlusIcon className="h-4 w-4 mr-2" />
                    </motion.div>
                    <span className="relative z-10">New Chat</span>
                  </Button>
                </motion.div>
              </motion.div>
            </div>

            {/* Sessions List */}
            <div className="flex-1 overflow-y-auto p-2">
              {sessions.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.3 }}
                  className="text-center py-8 text-foreground-muted"
                >
                  <motion.div
                    animate={{ 
                      rotate: 360,
                      scale: [1, 1.1, 1]
                    }}
                    transition={{ 
                      rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                      scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
                    }}
                  >
                    <MessageSquareIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  </motion.div>
                  <p>No conversations yet</p>
                  <p className="text-sm">Start a new chat to begin</p>
                </motion.div>
              ) : (
                <div className="space-y-1">
                  {sessions.map((session, index) => (
                    <motion.div
                      key={session.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                      onClick={() => handleSessionClick(session)}
                      className={`
                        group relative p-3 rounded-lg cursor-pointer transition-all duration-200
                        ${currentSession?.id === session.id 
                          ? 'bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20 shadow-lg' 
                          : 'hover:bg-gradient-to-r hover:from-accent/50 hover:to-accent/20 hover:scale-[1.02]'
                        }
                      `}
                      whileHover={{ y: -1 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <motion.div
                              animate={{ 
                                rotate: currentSession?.id === session.id ? 360 : 0,
                                scale: currentSession?.id === session.id ? [1, 1.2, 1] : 1
                              }}
                              transition={{ 
                                duration: currentSession?.id === session.id ? 2 : 0.3,
                                repeat: currentSession?.id === session.id ? Infinity : 0,
                                ease: "linear"
                              }}
                            >
                              <MessageSquareIcon className={`h-3 w-3 ${currentSession?.id === session.id ? 'text-primary' : 'text-foreground-muted'}`} />
                            </motion.div>
                            <h3 className="font-medium text-foreground truncate">
                              {session.title}
                            </h3>
                          </div>
                          <p className="text-sm text-foreground-secondary mt-1 flex items-center gap-1">
                            <ClockIcon className="h-3 w-3" />
                            {session.updatedAt ? formatDate(session.updatedAt) : 'Recent'}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <div className="flex items-center gap-1">
                              <div className="w-2 h-2 bg-primary/60 rounded-full animate-pulse" />
                              <p className="text-xs text-foreground-muted">
                                {session.messages.length} messages
                              </p>
                            </div>
                          </div>
                        </div>
                        <motion.div
                          initial={{ opacity: 0, scale: 0.8 }}
                          whileHover={{ opacity: 1, scale: 1 }}
                          className="group-hover:opacity-100 opacity-0 transition-all duration-200"
                        >
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => handleDeleteSession(e, session.id)}
                            className="h-8 w-8 hover:bg-destructive/20 hover:text-destructive"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </Button>
                        </motion.div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.4 }}
              className="p-4 border-t border-border/50 relative z-10 space-y-2"
            >
              {/* Settings Button */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Link href="/settings">
                  <Button
                    variant="ghost"
                    className="w-full justify-start hover:bg-gradient-to-r hover:from-accent/50 hover:to-accent/20 transition-all duration-200 relative overflow-hidden"
                  >
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/5 to-transparent"
                      animate={{ x: ['-100%', '100%'] }}
                      transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    />
                    <motion.div
                      whileHover={{ rotate: 180 }}
                      transition={{ duration: 0.3 }}
                      className="relative z-10"
                    >
                      <SettingsIcon className="h-4 w-4 mr-2" />
                    </motion.div>
                    <span className="relative z-10">Settings</span>
                  </Button>
                </Link>
              </motion.div>

              {/* Logout Button */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  variant="ghost"
                  onClick={handleLogout}
                  className="w-full justify-start hover:bg-gradient-to-r hover:from-destructive/20 hover:to-destructive/10 hover:text-destructive transition-all duration-200 relative overflow-hidden"
                >
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-destructive/5 to-transparent"
                    animate={{ x: ['-100%', '100%'] }}
                    transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
                  />
                  <motion.div
                    whileHover={{ x: 2 }}
                    transition={{ duration: 0.2 }}
                    className="relative z-10"
                  >
                    <LogOutIcon className="h-4 w-4 mr-2" />
                  </motion.div>
                  <span className="relative z-10">Logout</span>
                </Button>
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}