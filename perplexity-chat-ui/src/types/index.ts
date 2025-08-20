export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  chainOfThought?: ChainOfThoughtEvent[]
  agentOutputs?: { [agentId: string]: string }
}

export interface ChainOfThoughtEvent {
  type: string
  event?: string
  agent_id?: string
  agent_name?: string
  tool?: string
  content?: string
  timestamp?: string | number
  duration?: string
  raw?: string
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

export type AgentType = 'doc_agent' | 'web_agent' | 'reasoning_team'

export interface AgentInfo {
  id: string
  name: string
  description: string
  type: string
}

export interface ChatSettings {
  agent: AgentType
  temperature: number
  detailed_breakdown: boolean
}