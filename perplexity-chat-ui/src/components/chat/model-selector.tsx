'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useChatStore } from '@/store/chat-store'
import { AgentType } from '@/types'
import { 
  ChevronDownIcon,
  GlobeIcon,
  FileTextIcon,
  BrainIcon,
  SettingsIcon
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function AgentSelector() {
  const [isOpen, setIsOpen] = useState(false)
  const { settings, updateSettings } = useChatStore()

  const agents: { id: AgentType; name: string; icon: React.ReactNode; description: string; gradient: string }[] = [
    { 
      id: 'doc_agent', 
      name: 'Document Agent', 
      icon: <FileTextIcon className="h-4 w-4" />, 
      description: 'RAG Assistant with local document search capabilities',
      gradient: 'from-emerald-500 to-green-600' 
    },
    { 
      id: 'web_agent', 
      name: 'Web Agent', 
      icon: <GlobeIcon className="h-4 w-4" />, 
      description: 'Web search agent that helps users find the latest news and information',
      gradient: 'from-blue-500 to-cyan-600' 
    },
    { 
      id: 'reasoning_team', 
      name: 'Reasoning Team', 
      icon: <BrainIcon className="h-4 w-4" />, 
      description: 'Team that coordinates between document search and web search to provide comprehensive answers',
      gradient: 'from-purple-500 to-pink-600' 
    }
  ]

  const currentAgent = agents.find(a => a.id === settings.agent)

  return (
    <div className="relative">
      <motion.div
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="relative overflow-hidden rounded-lg"
      >
        <Button
          variant="outline"
          onClick={() => setIsOpen(!isOpen)}
          className={`w-full justify-between bg-gradient-to-r ${currentAgent?.gradient || 'from-background to-background-secondary'} border-border/50 backdrop-blur-sm hover:shadow-lg transition-all duration-300 relative overflow-hidden`}
        >
          {/* Animated background overlay */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
            animate={{
              x: isOpen ? 0 : '-100%',
            }}
            transition={{
              duration: 0.6,
              ease: "easeInOut"
            }}
          />
          
          <div className="flex items-center gap-2 relative z-10">
            <motion.div
              animate={{ rotate: isOpen ? 360 : 0 }}
              transition={{ duration: 0.3 }}
            >
              {currentAgent?.icon}
            </motion.div>
            <span className="text-sm font-medium text-white drop-shadow-sm">{currentAgent?.name}</span>
            {settings.detailed_breakdown && (
              <>
                <span className="text-xs text-white/70">•</span>
                <motion.div
                  animate={{ rotate: isOpen ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <SettingsIcon className="h-3 w-3" />
                </motion.div>
                <span className="text-xs text-white/80">Detailed</span>
              </>
            )}
          </div>
          <motion.div
            animate={{ rotate: isOpen ? 180 : 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <ChevronDownIcon className="h-4 w-4 text-white/90" />
          </motion.div>
        </Button>
      </motion.div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute top-full left-0 right-0 mt-2 bg-gradient-to-b from-background-secondary to-background border border-border/50 rounded-xl shadow-2xl backdrop-blur-sm z-50 overflow-hidden"
          >
            {/* Agent Selection */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
              className="p-4 border-b border-border/30"
            >
              <h3 className="text-sm font-semibold text-foreground mb-3 bg-gradient-to-r from-foreground to-foreground-secondary bg-clip-text text-transparent">
                AI Agent
              </h3>
              <div className="space-y-2">
                {agents.map((agent, index) => (
                  <motion.button
                    key={agent.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                    onClick={() => {
                      updateSettings({ agent: agent.id })
                    }}
                    whileHover={{ scale: 1.02, x: 4 }}
                    whileTap={{ scale: 0.98 }}
                    className={`w-full flex items-start gap-3 p-3 rounded-lg transition-all duration-200 relative overflow-hidden group ${
                      settings.agent === agent.id 
                        ? `bg-gradient-to-r ${agent.gradient} text-white shadow-lg` 
                        : 'hover:bg-gradient-to-r hover:from-accent/50 hover:to-accent/20 text-foreground'
                    }`}
                  >
                    {settings.agent === agent.id && (
                      <motion.div
                        layoutId="agent-selection"
                        className="absolute inset-0 bg-gradient-to-r from-white/20 to-white/10 rounded-lg"
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                      />
                    )}
                    <motion.div
                      animate={{ 
                        rotate: settings.agent === agent.id ? [0, 360] : 0,
                        scale: settings.agent === agent.id ? [1, 1.2, 1] : 1
                      }}
                      transition={{ 
                        duration: settings.agent === agent.id ? 0.6 : 0.2,
                        ease: "easeInOut"
                      }}
                      className="shrink-0 mt-0.5 relative z-10"
                    >
                      {agent.icon}
                    </motion.div>
                    <div className="flex-1 text-left relative z-10">
                      <div className="text-sm font-medium">{agent.name}</div>
                      <div className={`text-xs mt-1 ${
                        settings.agent === agent.id ? 'text-white/80' : 'text-foreground-muted'
                      }`}>
                        {agent.description}
                      </div>
                    </div>
                    {settings.agent === agent.id && (
                      <motion.div
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="ml-auto mt-1 w-2 h-2 bg-white rounded-full relative z-10"
                      />
                    )}
                  </motion.button>
                ))}
              </div>
            </motion.div>

            {/* Settings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
              className="p-4"
            >
              <h3 className="text-sm font-semibold text-foreground mb-3 bg-gradient-to-r from-foreground to-foreground-secondary bg-clip-text text-transparent">
                Options
              </h3>
              <div className="space-y-2">
                <motion.button
                  whileHover={{ scale: 1.02, x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    updateSettings({ detailed_breakdown: !settings.detailed_breakdown })
                    setIsOpen(false)
                  }}
                  className={`w-full flex items-start gap-3 p-3 rounded-lg transition-all duration-200 relative overflow-hidden group ${
                    settings.detailed_breakdown 
                      ? 'bg-gradient-to-r from-amber-400 to-orange-500 text-white shadow-lg' 
                      : 'hover:bg-gradient-to-r hover:from-accent/50 hover:to-accent/20 text-foreground'
                  }`}
                >
                  {settings.detailed_breakdown && (
                    <motion.div
                      layoutId="detailed-selection"
                      className="absolute inset-0 bg-gradient-to-r from-white/20 to-white/10 rounded-lg"
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                    />
                  )}
                  <motion.div
                    animate={{ 
                      rotate: settings.detailed_breakdown ? [0, 360] : 0,
                      scale: settings.detailed_breakdown ? [1, 1.2, 1] : 1
                    }}
                    transition={{ 
                      duration: settings.detailed_breakdown ? 0.6 : 0.2,
                      ease: "easeInOut"
                    }}
                    className="shrink-0 mt-0.5 relative z-10"
                  >
                    <SettingsIcon className="h-4 w-4" />
                  </motion.div>
                  <div className="flex-1 text-left relative z-10">
                    <div className="text-sm font-medium">Detailed Breakdown</div>
                    <div className={`text-xs mt-1 ${
                      settings.detailed_breakdown ? 'text-white/80' : 'text-foreground-muted'
                    }`}>
                      Show agent reasoning steps and tool calls
                    </div>
                  </div>
                  {settings.detailed_breakdown && (
                    <motion.div
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="ml-auto mt-1 w-2 h-2 bg-white rounded-full relative z-10"
                    />
                  )}
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}