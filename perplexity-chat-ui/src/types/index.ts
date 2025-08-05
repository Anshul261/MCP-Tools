export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  files?: FileAttachment[]
  isVoice?: boolean
}

export interface FileAttachment {
  id: string
  name: string
  size: number
  type: string
  url: string
}

export interface Session {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

export interface User {
  id: string
  email: string
  name: string
  avatar?: string
}

export type SearchMode = 'online' | 'local' | 'both'
export type ModelType = 'gpt-4' | 'claude-3' | 'gemini-pro' | 'local-llm'

export interface ChatSettings {
  model: ModelType
  searchMode: SearchMode
  temperature: number
}