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

export default function ModelSelector() {
  const [isOpen, setIsOpen] = useState(false)
  const { settings, updateSettings } = useChatStore()

  const models: { id: ModelType; name: string; icon: React.ReactNode }[] = [
    { id: 'gpt-4', name: 'GPT-4', icon: <BrainIcon className="h-4 w-4" /> },
    { id: 'claude-3', name: 'Claude 3', icon: <SparklesIcon className="h-4 w-4" /> },
    { id: 'gemini-pro', name: 'Gemini Pro', icon: <ZapIcon className="h-4 w-4" /> },
    { id: 'local-llm', name: 'Local LLM', icon: <HardDriveIcon className="h-4 w-4" /> },
  ]

  const searchModes: { id: SearchMode; name: string; icon: React.ReactNode; description: string }[] = [
    { 
      id: 'online', 
      name: 'Online Search', 
      icon: <GlobeIcon className="h-4 w-4" />,
      description: 'Search the web for latest information'
    },
    { 
      id: 'local', 
      name: 'Local Knowledge', 
      icon: <HardDriveIcon className="h-4 w-4" />,
      description: 'Use local documents and knowledge base'
    },
    { 
      id: 'both', 
      name: 'Combined Search', 
      icon: <CombineIcon className="h-4 w-4" />,
      description: 'Search both online and local sources'
    },
  ]

  const currentModel = models.find(m => m.id === settings.model)
  const currentSearchMode = searchModes.find(s => s.id === settings.searchMode)

  return (
    <div className="relative">
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full justify-between bg-input border-border hover:bg-accent"
      >
        <div className="flex items-center gap-2">
          {currentModel?.icon}
          <span className="text-sm">{currentModel?.name}</span>
          <span className="text-xs text-foreground-muted">•</span>
          {currentSearchMode?.icon}
          <span className="text-xs text-foreground-muted">{currentSearchMode?.name}</span>
        </div>
        <ChevronDownIcon className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-background-secondary border border-border rounded-lg shadow-lg z-50">
          {/* Model Selection */}
          <div className="p-3 border-b border-border">
            <h3 className="text-sm font-medium text-foreground mb-2">AI Model</h3>
            <div className="space-y-1">
              {models.map((model) => (
                <button
                  key={model.id}
                  onClick={() => {
                    updateSettings({ model: model.id })
                  }}
                  className={`w-full flex items-center gap-3 p-2 rounded hover:bg-accent transition-colors ${
                    settings.model === model.id ? 'bg-primary/10 text-primary' : 'text-foreground'
                  }`}
                >
                  {model.icon}
                  <span className="text-sm">{model.name}</span>
                  {settings.model === model.id && (
                    <div className="ml-auto w-2 h-2 bg-primary rounded-full" />
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Search Mode Selection */}
          <div className="p-3">
            <h3 className="text-sm font-medium text-foreground mb-2">Search Mode</h3>
            <div className="space-y-1">
              {searchModes.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => {
                    updateSettings({ searchMode: mode.id })
                    setIsOpen(false)
                  }}
                  className={`w-full flex items-start gap-3 p-2 rounded hover:bg-accent transition-colors ${
                    settings.searchMode === mode.id ? 'bg-primary/10 text-primary' : 'text-foreground'
                  }`}
                >
                  <div className="shrink-0 mt-0.5">{mode.icon}</div>
                  <div className="flex-1 text-left">
                    <div className="text-sm font-medium">{mode.name}</div>
                    <div className="text-xs text-foreground-muted">{mode.description}</div>
                  </div>
                  {settings.searchMode === mode.id && (
                    <div className="ml-auto mt-1 w-2 h-2 bg-primary rounded-full" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}