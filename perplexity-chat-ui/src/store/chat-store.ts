import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { Message, Session, ChatSettings } from '@/types'
import { generateId } from '@/lib/utils'

interface ChatState {
  currentSession: Session | null
  sessions: Session[]
  settings: ChatSettings
  isLoading: boolean
  isRecording: boolean
  
  // Actions
  createSession: () => void
  deleteSession: (sessionId: string) => void
  setCurrentSession: (session: Session) => void
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  sendMessage: (content: string, files?: File[]) => Promise<void>
  updateSettings: (settings: Partial<ChatSettings>) => void
  setLoading: (loading: boolean) => void
  setRecording: (recording: boolean) => void
  clearCurrentSession: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      currentSession: null,
      sessions: [],
      settings: {
        model: 'gpt-4',
        searchMode: 'both',
        temperature: 0.7,
      },
      isLoading: false,
      isRecording: false,

      createSession: () => {
        const now = new Date()
        const newSession: Session = {
          id: generateId(),
          title: 'New Chat',
          messages: [],
          createdAt: now,
          updatedAt: now,
        }
        
        set(state => ({
          sessions: [newSession, ...state.sessions],
          currentSession: newSession,
        }))
      },

      deleteSession: (sessionId: string) => {
        set(state => ({
          sessions: state.sessions.filter(s => s.id !== sessionId),
          currentSession: state.currentSession?.id === sessionId 
            ? state.sessions.find(s => s.id !== sessionId) || null 
            : state.currentSession,
        }))
      },

      setCurrentSession: (session: Session) => {
        set({ currentSession: session })
      },

      addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => {
        const now = new Date()
        const newMessage: Message = {
          ...message,
          id: generateId(),
          timestamp: now,
        }

        set(state => {
          if (!state.currentSession) return state

          const updatedSession: Session = {
            ...state.currentSession,
            messages: [...state.currentSession.messages, newMessage],
            title: state.currentSession.messages.length === 0 
              ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
              : state.currentSession.title,
            updatedAt: now,
          }

          return {
            currentSession: updatedSession,
            sessions: state.sessions.map(s => 
              s.id === updatedSession.id ? updatedSession : s
            ),
          }
        })
      },

      sendMessage: async (content: string, files?: File[]) => {
        const state = get()
        
        if (!state.currentSession) {
          state.createSession()
        }

        // Add user message
        const userMessage: Omit<Message, 'id' | 'timestamp'> = {
          content,
          role: 'user',
          files: files ? files.map(file => ({
            id: generateId(),
            name: file.name,
            size: file.size,
            type: file.type,
            url: URL.createObjectURL(file)
          })) : undefined,
        }

        state.addMessage(userMessage)
        state.setLoading(true)

        try {
          // Import API client dynamically to avoid issues
          const { apiClient } = await import('@/lib/api')
          
          // Send message to API
          const response = await apiClient.sendMessage({
            message: content,
            session_id: state.currentSession?.id,
            model: state.settings.model,
            search_mode: state.settings.searchMode,
            files: files,
          })

          // Add AI response
          const aiMessage: Omit<Message, 'id' | 'timestamp'> = {
            content: response.message,
            role: 'assistant',
          }

          state.addMessage(aiMessage)
        } catch (error) {
          console.error('Failed to send message:', error)
          
          // Add error message
          const errorMessage: Omit<Message, 'id' | 'timestamp'> = {
            content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            role: 'assistant',
          }
          state.addMessage(errorMessage)
        } finally {
          state.setLoading(false)
        }
      },

      updateSettings: (newSettings: Partial<ChatSettings>) => {
        set(state => ({
          settings: { ...state.settings, ...newSettings }
        }))
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      setRecording: (recording: boolean) => {
        set({ isRecording: recording })
      },

      clearCurrentSession: () => {
        set({ currentSession: null })
      },
    }),
    {
      name: 'chat-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        sessions: state.sessions,
        settings: state.settings,
      }),
    }
  )
)