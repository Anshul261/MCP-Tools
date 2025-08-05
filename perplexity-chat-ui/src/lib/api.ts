// API client for FastAPI backend integration

import { Session } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatRequest {
  message: string
  session_id?: string
  model: string
  search_mode: 'online' | 'local' | 'both'
  files?: File[]
}

export interface ChatResponse {
  message: string
  session_id: string
  sources?: string[]
  model_used: string
}

export interface AuthRequest {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    email: string
    name: string
  }
}

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token')
    }
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
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

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
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

  // Authentication endpoints
  async login(credentials: AuthRequest): Promise<AuthResponse> {
    // Try JSON login first (our custom endpoint)
    try {
      const response = await fetch(`${this.baseURL}/auth/login-json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (response.ok) {
        const data = await response.json()
        this.setToken(data.access_token)
        return data
      }
    } catch {
      // Fall back to form data method
    }

    // Fallback to form data method
    const formData = new FormData()
    formData.append('username', credentials.email)
    formData.append('password', credentials.password)

    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Login failed')
    }

    const data = await response.json()
    this.setToken(data.access_token)
    return data
  }

  async register(userData: AuthRequest & { name: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  async logout(): Promise<void> {
    this.clearToken()
  }

  // Chat endpoints
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    if (request.files && request.files.length > 0) {
      // Handle file uploads
      const formData = new FormData()
      formData.append('message', request.message)
      formData.append('model', request.model)
      formData.append('search_mode', request.search_mode)
      
      if (request.session_id) {
        formData.append('session_id', request.session_id)
      }

      request.files.forEach((file) => {
        formData.append(`files`, file)
      })

      const response = await fetch(`${this.baseURL}/files/upload-and-chat`, {
        method: 'POST',
        headers: this.token ? { Authorization: `Bearer ${this.token}` } : {},
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to send message with files')
      }

      return response.json()
    } else {
      // Regular text message
      return this.request<ChatResponse>('/chat/message', {
        method: 'POST',
        body: JSON.stringify(request),
      })
    }
  }

  async getSessions(): Promise<Session[]> {
    return this.request<Session[]>('/chat/sessions')
  }

  async getSession(sessionId: string): Promise<Session> {
    return this.request<Session>(`/chat/sessions/${sessionId}`)
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.request<void>(`/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    })
  }

  // Voice endpoints
  async transcribeAudio(audioBlob: Blob): Promise<{ text: string }> {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')

    const response = await fetch(`${this.baseURL}/voice/transcribe`, {
      method: 'POST',
      headers: this.token ? { Authorization: `Bearer ${this.token}` } : {},
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Failed to transcribe audio')
    }

    return response.json()
  }

  async synthesizeVoice(text: string): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/voice/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      },
      body: JSON.stringify({ text }),
    })

    if (!response.ok) {
      throw new Error('Failed to synthesize voice')
    }

    return response.blob()
  }
}

export const apiClient = new ApiClient()
export default apiClient