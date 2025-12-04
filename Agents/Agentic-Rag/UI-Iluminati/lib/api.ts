/**
 * API Configuration for AgentOS Integration
 * Handles communication with the simple document agent
 */

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7777"
const AGENT_ID = "doc-agent"

export interface AgentResponse {
  content: string
  run_id?: string
  session_id?: string
  error?: string
}

/**
 * Send a message to the document agent (general chat mode)
 * @param message - User's message
 * @param files - Optional files to upload with the message
 * @param sessionId - Optional session ID for conversation history
 * @returns Agent's response
 */
export async function sendMessageToAgent(
  message: string,
  files?: File[],
  sessionId?: string
): Promise<AgentResponse> {
  try {
    const formData = new FormData()
    formData.append("message", message)
    formData.append("stream", "false") // Non-streaming for simplicity

    if (sessionId) {
      formData.append("session_id", sessionId)
    }

    // Attach files if provided
    if (files && files.length > 0) {
      console.log(`[API] Uploading ${files.length} file(s):`, files.map(f => f.name))
      files.forEach((file) => {
        formData.append("files", file)
        console.log(`[API] Added file: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`)
      })
    } else {
      console.log("[API] No files to upload")
    }

    console.log(`[API] Sending request to: ${API_BASE_URL}/agents/${AGENT_ID}/runs`)
    console.log(`[API] Session ID: ${sessionId || "none"}`)

    const response = await fetch(`${API_BASE_URL}/agents/${AGENT_ID}/runs`, {
      method: "POST",
      body: formData,
    })

    console.log(`[API] Response status: ${response.status}`)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `API Error: ${response.status}`)
    }

    const data = await response.json()

    // Extract content from the response
    // AGNO returns: { content: "...", run_id: "...", ... }
    return {
      content: data.content || data.message || "No response from agent",
      run_id: data.run_id,
      session_id: data.session_id,
    }
  } catch (error) {
    console.error("Error calling agent API:", error)
    return {
      content: "",
      error: error instanceof Error ? error.message : "Failed to get response from agent",
    }
  }
}

/**
 * Check if the API is healthy
 */
export async function checkAPIHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    return response.ok
  } catch (error) {
    console.error("API health check failed:", error)
    return false
  }
}

/**
 * Get API information
 */
export async function getAPIInfo(): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/info`)
    if (!response.ok) return null
    return await response.json()
  } catch (error) {
    console.error("Failed to get API info:", error)
    return null
  }
}
