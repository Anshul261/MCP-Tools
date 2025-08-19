// API client for agent-api-main integration

import { Session } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatRequest {
  message: string
  user_id?: string
  session_id?: string
  stream?: boolean
  debug_mode?: boolean
  detailed_breakdown?: boolean
}

export interface ChatResponse {
  response: string
  session_id: string
  user_id: string
  agent_id: string
}

export interface AgentInfo {
  id: string
  name: string
  description: string
  type: string
}

export interface HealthResponse {
  status: string
  api: {
    name: string
    version: string
    debug: boolean
  }
  database: {
    database: string
    vector_db: string
    embedder: string
    knowledge_base: string
  }
  documents: {
    status: string
    total_documents: number
    converted_documents: number
    knowledge_base_loaded: boolean
  }
  configuration: {
    status: string
  }
}

class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Health endpoint
  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/v1/health')
  }

  // Agent endpoints
  async getAgents(): Promise<string[]> {
    return this.request<string[]>('/v1/agents')
  }

  async getAgentsInfo(): Promise<AgentInfo[]> {
    return this.request<AgentInfo[]>('/v1/agents/info')
  }

  async getAgentInfo(agentId: string): Promise<AgentInfo> {
    return this.request<AgentInfo>(`/v1/agents/${agentId}/info`)
  }

  async validateAgent(agentId: string): Promise<{ valid: boolean; agent_id: string; type: string; name: string; error?: string }> {
    return this.request(`/v1/agents/${agentId}/validate`)
  }

  // Chat with agent - streaming
  async sendMessageStream(agentId: string, request: ChatRequest): Promise<ReadableStream<Uint8Array> | null> {
    const url = `${this.baseURL}/v1/agents/${agentId}/chat`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const body = {
      ...request,
      stream: true
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    return response.body
  }

  // Chat with agent - non-streaming
  async sendMessage(agentId: string, request: ChatRequest): Promise<ChatResponse> {
    const body = {
      ...request,
      stream: false
    }

    return this.request<ChatResponse>(`/v1/agents/${agentId}/chat`, {
      method: 'POST',
      body: JSON.stringify(body),
    })
  }

  // Document endpoints
  async getDocumentStats(): Promise<{
    total_documents: number
    converted_documents: number
    total_size_bytes: number
    knowledge_base_loaded: boolean
    source_directory: string
    converted_directory: string
  }> {
    return this.request('/v1/documents/stats')
  }

  async getDocuments(): Promise<Array<{
    filename: string
    size: number
    converted: boolean
    converted_path: string
    extension: string
    valid: boolean
  }>> {
    return this.request('/v1/documents')
  }

  async uploadDocuments(files: File[]): Promise<{
    message: string
    uploaded_files: Array<{ filename: string; size: number; success: boolean }>
    failed_files: string[]
    total_uploaded: number
    total_failed: number
  }> {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await fetch(`${this.baseURL}/v1/documents/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Failed to upload documents')
    }

    return response.json()
  }

  async processDocuments(): Promise<{
    message: string
    total_files: number
    converted: number
    failed: number
    knowledge_base_reloaded: boolean
  }> {
    return this.request('/v1/documents/process', {
      method: 'POST',
    })
  }

  async deleteDocument(filename: string): Promise<{ message: string }> {
    return this.request(`/v1/documents/${filename}`, {
      method: 'DELETE',
    })
  }
}

export const apiClient = new ApiClient()
export default apiClient