import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { Message, Session, ChatSettings } from '@/types'
import { generateId } from '@/lib/utils'

interface ChatState {
  currentSession: Session | null
  sessions: Session[]
  settings: ChatSettings
  isLoading: boolean
  
  // Actions
  createSession: () => void
  deleteSession: (sessionId: string) => void
  setCurrentSession: (session: Session) => void
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  updateLastMessage: (content: string) => void
  sendMessage: (content: string) => Promise<void>
  sendMessageStream: (content: string) => Promise<void>
  updateSettings: (settings: Partial<ChatSettings>) => void
  setLoading: (loading: boolean) => void
  clearCurrentSession: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      currentSession: null,
      sessions: [],
      settings: {
        agent: 'reasoning_team',
        temperature: 0.7,
        detailed_breakdown: true,
      },
      isLoading: false,

      createSession: () => {
        const now = new Date()
        // Use agent-api-main compatible session ID format
        const sessionId = `session_${now.getFullYear()}${(now.getMonth() + 1).toString().padStart(2, '0')}${now.getDate().toString().padStart(2, '0')}_${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}${now.getSeconds().toString().padStart(2, '0')}_${generateId().slice(0, 8)}`
        
        const newSession: Session = {
          id: sessionId,
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

      updateLastMessage: (content: string) => {
        set(state => {
          if (!state.currentSession || state.currentSession.messages.length === 0) return state

          const messages = [...state.currentSession.messages]
          const lastMessage = messages[messages.length - 1]
          
          messages[messages.length - 1] = {
            ...lastMessage,
            content: content,
            timestamp: new Date(),
          }

          const updatedSession: Session = {
            ...state.currentSession,
            messages,
            updatedAt: new Date(),
          }

          return {
            currentSession: updatedSession,
            sessions: state.sessions.map(s => 
              s.id === updatedSession.id ? updatedSession : s
            ),
          }
        })
      },

      sendMessage: async (content: string) => {
        // Use streaming by default for better UX
        return get().sendMessageStream(content)
      },

      sendMessageStream: async (content: string) => {
        const state = get()
        
        if (!state.currentSession) {
          state.createSession()
        }

        // Add user message
        const userMessage: Omit<Message, 'id' | 'timestamp'> = {
          content,
          role: 'user',
        }

        state.addMessage(userMessage)
        state.setLoading(true)

        // Add empty AI message that will be updated with streaming content
        const aiMessage: Omit<Message, 'id' | 'timestamp'> = {
          content: '',
          role: 'assistant',
        }
        state.addMessage(aiMessage)

        try {
          // Import API client dynamically to avoid issues
          const { apiClient } = await import('@/lib/api')
          
          // Send message to agent with streaming
          const stream = await apiClient.sendMessageStream(state.settings.agent, {
            message: content,
            user_id: 'default_user', // TODO: Get from auth
            session_id: state.currentSession?.id,
            stream: true,
            debug_mode: false,
            detailed_breakdown: state.settings.detailed_breakdown,
          })

          if (stream) {
            const reader = stream.getReader()
            const decoder = new TextDecoder()
            let accumulatedContent = ''

            while (true) {
              const { done, value } = await reader.read()
              if (done) break

              const chunk = decoder.decode(value, { stream: true })
              const lines = chunk.split('\n')

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  const data = line.slice(6).trim()
                  if (data === '[DONE]') {
                    break
                  }
                  
                  // For simple streaming, just accumulate the text
                  // For detailed breakdown, we'd need to parse JSON events
                  if (data && !data.startsWith('{')) {
                    accumulatedContent += data
                    state.updateLastMessage(accumulatedContent)
                  } else if (data.startsWith('{')) {
                    // Handle detailed breakdown JSON events
                    try {
                      // Skip detailed events for now, just get the content
                      if (data.includes('"content"') && !data.includes('"event"')) {
                        accumulatedContent += data
                        state.updateLastMessage(accumulatedContent)
                      }
                    } catch (e) {
                      // Skip invalid JSON
                    }
                  }
                }
              }
            }
          }
        } catch (error) {
          console.error('Failed to send streaming message:', error)
          
          // Update the last message with error
          const errorContent = `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`
          state.updateLastMessage(errorContent)
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