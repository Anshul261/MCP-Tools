'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useChatStore } from '@/store/chat-store'
import { SearchMode, ModelType } from '@/types'
import { 
  ChevronDownIcon,
  GlobeIcon,
  HardDriveIcon,
  CombineIcon,
  BrainIcon,
  ZapIcon,
  SparklesIcon
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function ModelSelector() {
  const [isOpen, setIsOpen] = useState(false)
  const { settings, updateSettings } = useChatStore()

  const models: { id: ModelType; name: string; icon: React.ReactNode; gradient: string }[] = [
    { 
      id: 'gpt-4', 
      name: 'GPT-4', 
      icon: <BrainIcon className="h-4 w-4" />, 
      gradient: 'from-blue-500 to-purple-600' 
    },
    { 
      id: 'claude-3', 
      name: 'Claude 3', 
      icon: <SparklesIcon className="h-4 w-4" />, 
      gradient: 'from-orange-500 to-pink-600' 
    },
    { 
      id: 'gemini-pro', 
      name: 'Gemini Pro', 
      icon: <ZapIcon className="h-4 w-4" />, 
      gradient: 'from-green-500 to-teal-600' 
    },
    { 
      id: 'local-llm', 
      name: 'Local LLM', 
      icon: <HardDriveIcon className="h-4 w-4" />, 
      gradient: 'from-gray-500 to-slate-600' 
    },
  ]

  const searchModes: { id: SearchMode; name: string; icon: React.ReactNode; description: string; gradient: string }[] = [
    { 
      id: 'online', 
      name: 'Online Search', 
      icon: <GlobeIcon className="h-4 w-4" />,
      description: 'Search the web for latest information',
      gradient: 'from-blue-400 to-cyan-500'
    },
    { 
      id: 'local', 
      name: 'Local Knowledge', 
      icon: <HardDriveIcon className="h-4 w-4" />,
      description: 'Use local documents and knowledge base',
      gradient: 'from-emerald-400 to-green-500'
    },
    { 
      id: 'both', 
      name: 'Combined Search', 
      icon: <CombineIcon className="h-4 w-4" />,
      description: 'Search both online and local sources',
      gradient: 'from-purple-400 to-pink-500'
    },
  ]

  const currentModel = models.find(m => m.id === settings.model)
  const currentSearchMode = searchModes.find(s => s.id === settings.searchMode)

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
          className={`w-full justify-between bg-gradient-to-r ${currentModel?.gradient || 'from-background to-background-secondary'} border-border/50 backdrop-blur-sm hover:shadow-lg transition-all duration-300 relative overflow-hidden`}
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
              {currentModel?.icon}
            </motion.div>
            <span className="text-sm font-medium text-white drop-shadow-sm">{currentModel?.name}</span>
            <span className="text-xs text-white/70">•</span>
            <motion.div
              animate={{ rotate: isOpen ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              {currentSearchMode?.icon}
            </motion.div>
            <span className="text-xs text-white/80">{currentSearchMode?.name}</span>
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
            {/* Model Selection */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
              className="p-4 border-b border-border/30"
            >
              <h3 className="text-sm font-semibold text-foreground mb-3 bg-gradient-to-r from-foreground to-foreground-secondary bg-clip-text text-transparent">
                AI Model
              </h3>
              <div className="space-y-2">
                {models.map((model, index) => (
                  <motion.button
                    key={model.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                    onClick={() => {
                      updateSettings({ model: model.id })
                    }}
                    whileHover={{ scale: 1.02, x: 4 }}
                    whileTap={{ scale: 0.98 }}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200 relative overflow-hidden group ${
                      settings.model === model.id 
                        ? `bg-gradient-to-r ${model.gradient} text-white shadow-lg` 
                        : 'hover:bg-gradient-to-r hover:from-accent/50 hover:to-accent/20 text-foreground'
                    }`}
                  >
                    {settings.model === model.id && (
                      <motion.div
                        layoutId="model-selection"
                        className="absolute inset-0 bg-gradient-to-r from-white/20 to-white/10 rounded-lg"
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                      />
                    )}
                    <motion.div
                      animate={{ 
                        rotate: settings.model === model.id ? [0, 360] : 0,
                        scale: settings.model === model.id ? [1, 1.2, 1] : 1
                      }}
                      transition={{ 
                        duration: settings.model === model.id ? 0.6 : 0.2,
                        ease: "easeInOut"
                      }}
                      className="relative z-10"
                    >
                      {model.icon}
                    </motion.div>
                    <span className="text-sm font-medium relative z-10">{model.name}</span>
                    {settings.model === model.id && (
                      <motion.div
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="ml-auto w-2 h-2 bg-white rounded-full relative z-10"
                      />
                    )}
                  </motion.button>
                ))}
              </div>
            </motion.div>

            {/* Search Mode Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
              className="p-4"
            >
              <h3 className="text-sm font-semibold text-foreground mb-3 bg-gradient-to-r from-foreground to-foreground-secondary bg-clip-text text-transparent">
                Search Mode
              </h3>
              <div className="space-y-2">
                {searchModes.map((mode, index) => (
                  <motion.button
                    key={mode.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                    onClick={() => {
                      updateSettings({ searchMode: mode.id })
                      setIsOpen(false)
                    }}
                    whileHover={{ scale: 1.02, x: 4 }}
                    whileTap={{ scale: 0.98 }}
                    className={`w-full flex items-start gap-3 p-3 rounded-lg transition-all duration-200 relative overflow-hidden group ${
                      settings.searchMode === mode.id 
                        ? `bg-gradient-to-r ${mode.gradient} text-white shadow-lg` 
                        : 'hover:bg-gradient-to-r hover:from-accent/50 hover:to-accent/20 text-foreground'
                    }`}
                  >
                    {settings.searchMode === mode.id && (
                      <motion.div
                        layoutId="search-selection"
                        className="absolute inset-0 bg-gradient-to-r from-white/20 to-white/10 rounded-lg"
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                      />
                    )}
                    <motion.div
                      animate={{ 
                        rotate: settings.searchMode === mode.id ? [0, 360] : 0,
                        scale: settings.searchMode === mode.id ? [1, 1.2, 1] : 1
                      }}
                      transition={{ 
                        duration: settings.searchMode === mode.id ? 0.6 : 0.2,
                        ease: "easeInOut"
                      }}
                      className="shrink-0 mt-0.5 relative z-10"
                    >
                      {mode.icon}
                    </motion.div>
                    <div className="flex-1 text-left relative z-10">
                      <div className="text-sm font-medium">{mode.name}</div>
                      <div className={`text-xs mt-1 ${
                        settings.searchMode === mode.id ? 'text-white/80' : 'text-foreground-muted'
                      }`}>
                        {mode.description}
                      </div>
                    </div>
                    {settings.searchMode === mode.id && (
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
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}