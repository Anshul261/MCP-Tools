"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import {
  Send,
  Sparkles,
  ArrowRight,
  MessageSquare,
  Plus,
  Clock,
  ChevronLeft,
  ChevronRight,
  Sun,
  Moon,
  Paperclip,
  FolderOpen,
  X,
  Upload,
  FileText,
  Trash2,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
}

interface ChatHistory {
  id: string
  title: string
  timestamp: string
  preview: string
  projectId?: string
}

interface Project {
  id: string
  name: string
  description: string
  chatCount: number
  files: UploadedFile[]
}

interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isDark, setIsDark] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [activeTab, setActiveTab] = useState<"chats" | "projects">("chats")
  const [showNewProjectModal, setShowNewProjectModal] = useState(false)
  const [newProjectName, setNewProjectName] = useState("")
  const [newProjectDescription, setNewProjectDescription] = useState("")
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [projects, setProjects] = useState<Project[]>([
    { id: "1", name: "E-commerce App", description: "Building an online store", chatCount: 5, files: [] },
    { id: "2", name: "Dashboard UI", description: "Admin panel design", chatCount: 3, files: [] },
    { id: "3", name: "API Documentation", description: "REST API specs", chatCount: 2, files: [] },
  ])

  const [chatHistory] = useState<ChatHistory[]>([
    {
      id: "1",
      title: "Code Review Help",
      timestamp: "Today",
      preview: "Can you review my React component...",
      projectId: "1",
    },
    {
      id: "2",
      title: "API Integration",
      timestamp: "Yesterday",
      preview: "How do I connect to a REST API...",
      projectId: "2",
    },
    {
      id: "3",
      title: "Database Design",
      timestamp: "2 days ago",
      preview: "What's the best schema for...",
    },
    { id: "4", title: "CSS Animations", timestamp: "Last week", preview: "How can I create smooth transitions..." },
  ])

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [isDark])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "Thank you for your message. I'm here to help you with any questions or tasks you might have. Feel free to ask me anything!",
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1000)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleFileUpload = () => {
    fileInputRef.current?.click()
  }

  const handleCreateProject = () => {
    if (!newProjectName.trim()) return

    const newProject: Project = {
      id: Date.now().toString(),
      name: newProjectName,
      description: newProjectDescription,
      chatCount: 0,
      files: [],
    }

    setProjects((prev) => [newProject, ...prev])
    setNewProjectName("")
    setNewProjectDescription("")
    setShowNewProjectModal(false)
    setSelectedProject(newProject)
  }

  const handleProjectFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedProject || !e.target.files) return

    const files = Array.from(e.target.files)
    const uploadedFiles: UploadedFile[] = files.map((file) => ({
      id: Date.now().toString() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
    }))

    setProjects((prev) =>
      prev.map((p) => (p.id === selectedProject.id ? { ...p, files: [...p.files, ...uploadedFiles] } : p)),
    )

    setSelectedProject((prev) => (prev ? { ...prev, files: [...prev.files, ...uploadedFiles] } : null))
  }

  const handleRemoveFile = (fileId: string) => {
    if (!selectedProject) return

    setProjects((prev) =>
      prev.map((p) => (p.id === selectedProject.id ? { ...p, files: p.files.filter((f) => f.id !== fileId) } : p)),
    )

    setSelectedProject((prev) => (prev ? { ...prev, files: prev.files.filter((f) => f.id !== fileId) } : null))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B"
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
    return (bytes / (1024 * 1024)).toFixed(1) + " MB"
  }

  const filteredChats = selectedProject
    ? chatHistory.filter((chat) => chat.projectId === selectedProject.id)
    : chatHistory

  return (
    <div className="flex h-screen">
      <aside
        className={cn(
          "bg-sidebar border-r border-sidebar-border flex flex-col transition-all duration-300 shrink-0",
          sidebarOpen ? "w-72" : "w-0 overflow-hidden",
        )}
      >
        <div className="p-4 border-b border-sidebar-border space-y-3">
          <Button
            variant="outline"
            onClick={() => {
              setSelectedProject(null)
              setMessages([])
            }}
            className="w-full justify-start gap-2 font-mono text-xs uppercase tracking-wider rounded-sm bg-transparent border-border hover:bg-sidebar-accent"
          >
            <Plus className="w-4 h-4" />
            New Chat
          </Button>

          <div className="flex gap-1 p-1 bg-sidebar-accent rounded-sm border border-sidebar-border">
            <button
              onClick={() => setActiveTab("chats")}
              className={cn(
                "flex-1 font-mono text-xs uppercase tracking-wider py-2 rounded-sm transition-colors",
                activeTab === "chats" ? "bg-card border border-border text-foreground" : "text-muted-foreground",
              )}
            >
              Chats
            </button>
            <button
              onClick={() => setActiveTab("projects")}
              className={cn(
                "flex-1 font-mono text-xs uppercase tracking-wider py-2 rounded-sm transition-colors",
                activeTab === "projects" ? "bg-card border border-border text-foreground" : "text-muted-foreground",
              )}
            >
              Projects
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === "chats" ? (
            <>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground mb-4">
                {selectedProject ? `${selectedProject.name} Chats` : "Recent Chats"}
              </h3>
              <div className="space-y-2">
                {filteredChats.map((chat) => (
                  <button
                    key={chat.id}
                    className="w-full text-left p-3 rounded-sm border border-transparent hover:bg-sidebar-accent hover:border-sidebar-border transition-colors group"
                  >
                    <div className="flex items-start gap-3">
                      <MessageSquare className="w-4 h-4 text-muted-foreground mt-0.5 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-serif text-sm font-medium text-sidebar-foreground truncate">{chat.title}</p>
                        <p className="font-mono text-xs text-muted-foreground truncate mt-1">{chat.preview}</p>
                        <div className="flex items-center gap-1 mt-2">
                          <Clock className="w-3 h-3 text-muted-foreground" />
                          <span className="font-mono text-xs text-muted-foreground">{chat.timestamp}</span>
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground mb-4">Your Projects</h3>
              <div className="space-y-2">
                <button
                  onClick={() => setShowNewProjectModal(true)}
                  className="w-full p-3 rounded-sm border border-dashed border-border hover:bg-sidebar-accent hover:border-primary/30 transition-colors"
                >
                  <div className="flex items-center gap-3 justify-center">
                    <Plus className="w-4 h-4 text-primary" />
                    <span className="font-mono text-xs uppercase tracking-wider text-primary">New Project</span>
                  </div>
                </button>

                {projects.map((project) => (
                  <button
                    key={project.id}
                    onClick={() => {
                      setSelectedProject(project)
                      setActiveTab("chats")
                    }}
                    className={cn(
                      "w-full text-left p-3 rounded-sm border transition-colors group",
                      selectedProject?.id === project.id
                        ? "bg-sidebar-accent border-primary"
                        : "border-transparent hover:bg-sidebar-accent hover:border-sidebar-border",
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <FolderOpen className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-serif text-sm font-medium text-sidebar-foreground truncate">
                          {project.name}
                        </p>
                        <p className="font-mono text-xs text-muted-foreground truncate mt-1">{project.description}</p>
                        <div className="flex items-center gap-3 mt-2">
                          <span className="font-mono text-xs text-muted-foreground">{project.chatCount} chats</span>
                          <span className="font-mono text-xs text-muted-foreground">{project.files.length} files</span>
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="p-4 border-t border-sidebar-border">
          <div className="font-mono text-xs text-muted-foreground uppercase tracking-wider text-center">
            {activeTab === "chats" ? `${filteredChats.length} Conversations` : `${projects.length} Projects`}
          </div>
        </div>
      </aside>

      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-card border border-border rounded-r-sm p-1.5 hover:bg-secondary transition-colors"
        style={{ left: sidebarOpen ? "18rem" : "0" }}
      >
        {sidebarOpen ? (
          <ChevronLeft className="w-4 h-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
        )}
        <span className="sr-only">Toggle sidebar</span>
      </button>

      <div className="flex flex-col flex-1 min-w-0">
        <header className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div className="flex items-center gap-3">
            {selectedProject ? (
              <>
                <button
                  onClick={() => setSelectedProject(null)}
                  className="p-2 rounded-sm hover:bg-secondary transition-colors"
                  aria-label="Back to all chats"
                >
                  <ChevronLeft className="w-4 h-4 text-muted-foreground" />
                </button>
                <div>
                  <h1 className="font-serif text-2xl font-bold text-primary tracking-tight">{selectedProject.name}</h1>
                  <p className="font-mono text-xs text-muted-foreground uppercase tracking-widest">
                    {selectedProject.description}
                  </p>
                </div>
              </>
            ) : (
              <>
                <div className="w-8 h-8 rounded-sm bg-primary flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-primary-foreground" />
                </div>
                <h1 className="font-serif text-2xl font-bold text-primary tracking-tight">AI Assistant</h1>
              </>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsDark(!isDark)}
              className="p-2 rounded-sm border border-border hover:bg-secondary transition-colors"
              aria-label="Toggle theme"
            >
              {isDark ? (
                <Sun className="w-4 h-4 text-muted-foreground" />
              ) : (
                <Moon className="w-4 h-4 text-muted-foreground" />
              )}
            </button>
            <span className="font-mono text-xs text-muted-foreground uppercase tracking-widest">v1.0</span>
          </div>
        </header>

        {selectedProject && (
          <div className="border-b border-border bg-card p-4">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Project Files</h3>
                <label className="cursor-pointer">
                  <input type="file" multiple className="hidden" onChange={handleProjectFileUpload} />
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-sm border border-border hover:bg-secondary transition-colors">
                    <Upload className="w-3 h-3 text-primary" />
                    <span className="font-mono text-xs uppercase tracking-wider text-primary">Upload</span>
                  </div>
                </label>
              </div>

              {selectedProject.files.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                  {selectedProject.files.map((file) => (
                    <div
                      key={file.id}
                      className="p-3 rounded-sm border border-border bg-background group hover:border-primary/30 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <FileText className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                        <button
                          onClick={() => handleRemoveFile(file.id)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-destructive/10 rounded-sm"
                          aria-label="Remove file"
                        >
                          <Trash2 className="w-3 h-3 text-destructive" />
                        </button>
                      </div>
                      <p className="font-mono text-xs text-foreground truncate mt-2" title={file.name}>
                        {file.name}
                      </p>
                      <p className="font-mono text-xs text-muted-foreground mt-1">{formatFileSize(file.size)}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 border border-dashed border-border rounded-sm">
                  <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
                    No files uploaded yet
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto px-6 py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-sm bg-primary/10 flex items-center justify-center mb-6">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <h2 className="font-serif text-4xl font-bold text-primary mb-4 tracking-tight">The AI Assistant</h2>
              <p className="font-mono text-sm text-muted-foreground uppercase tracking-widest max-w-md leading-relaxed">
                Your intelligent conversation partner. Ask me anything to get started.
              </p>
              <div className="mt-8 flex flex-wrap gap-3 justify-center">
                {["Explain a concept", "Write some code", "Help me brainstorm"].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInput(suggestion)}
                    className="font-mono text-xs uppercase tracking-wider px-4 py-2 border border-border rounded-sm hover:bg-secondary hover:border-primary/30 transition-colors flex items-center gap-2 group"
                  >
                    {suggestion}
                    <ArrowRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity text-primary" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn("flex gap-4", message.role === "user" ? "justify-end" : "justify-start")}
                >
                  {message.role === "assistant" && (
                    <div className="w-8 h-8 rounded-sm bg-primary flex items-center justify-center shrink-0">
                      <Sparkles className="w-4 h-4 text-primary-foreground" />
                    </div>
                  )}
                  <div
                    className={cn(
                      "max-w-[70%] px-4 py-3 rounded-sm",
                      message.role === "user" ? "bg-primary text-primary-foreground" : "bg-card border border-border",
                    )}
                  >
                    <p className={cn("text-sm leading-relaxed", message.role === "user" ? "font-sans" : "font-serif")}>
                      {message.content}
                    </p>
                  </div>
                  {message.role === "user" && (
                    <div className="w-8 h-8 rounded-sm bg-muted flex items-center justify-center shrink-0">
                      <div className="w-4 h-4 rounded-full bg-primary" />
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-sm bg-primary flex items-center justify-center shrink-0">
                    <Sparkles className="w-4 h-4 text-primary-foreground" />
                  </div>
                  <div className="max-w-[70%] px-4 py-3 rounded-sm bg-card border border-border">
                    <div className="flex gap-1">
                      <div
                        className="w-2 h-2 rounded-full bg-primary animate-bounce"
                        style={{ animationDelay: "0s" }}
                      />
                      <div
                        className="w-2 h-2 rounded-full bg-primary animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      />
                      <div
                        className="w-2 h-2 rounded-full bg-primary animate-bounce"
                        style={{ animationDelay: "0.4s" }}
                      />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="border-t border-border p-4">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="relative bg-card border border-border rounded-sm overflow-hidden focus-within:border-primary transition-colors">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message here..."
                className="w-full bg-transparent px-4 py-3 pr-24 font-serif text-sm resize-none focus:outline-none placeholder:text-muted-foreground"
                rows={1}
                style={{
                  minHeight: "52px",
                  maxHeight: "200px",
                }}
              />
              <div className="absolute right-2 bottom-2 flex items-center gap-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  className="hidden"
                  onChange={(e) => {
                    console.log("[v0] Files selected:", e.target.files)
                  }}
                />
                <button
                  type="button"
                  onClick={handleFileUpload}
                  className="p-2 rounded-sm hover:bg-secondary transition-colors"
                  aria-label="Attach file"
                >
                  <Paperclip className="w-4 h-4 text-muted-foreground" />
                </button>
                <Button
                  type="submit"
                  size="sm"
                  disabled={!input.trim() || isLoading}
                  className="font-mono text-xs uppercase tracking-wider rounded-sm bg-primary hover:bg-primary/90 disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <p className="font-mono text-xs text-muted-foreground text-center mt-3 uppercase tracking-widest">
              Press Enter to send • Shift + Enter for new line
            </p>
          </form>
        </div>
      </div>

      {showNewProjectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card border border-border rounded-sm max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-serif text-xl font-bold text-primary">Create New Project</h2>
              <button
                onClick={() => {
                  setShowNewProjectModal(false)
                  setNewProjectName("")
                  setNewProjectDescription("")
                }}
                className="p-1 rounded-sm hover:bg-secondary transition-colors"
                aria-label="Close modal"
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label
                  htmlFor="project-name"
                  className="block font-mono text-xs uppercase tracking-wider text-muted-foreground mb-2"
                >
                  Project Name
                </label>
                <input
                  id="project-name"
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="Enter project name..."
                  className="w-full px-3 py-2 bg-background border border-border rounded-sm font-serif text-sm focus:outline-none focus:border-primary transition-colors"
                  autoFocus
                />
              </div>

              <div>
                <label
                  htmlFor="project-description"
                  className="block font-mono text-xs uppercase tracking-wider text-muted-foreground mb-2"
                >
                  Description
                </label>
                <textarea
                  id="project-description"
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  placeholder="Enter project description..."
                  className="w-full px-3 py-2 bg-background border border-border rounded-sm font-serif text-sm resize-none focus:outline-none focus:border-primary transition-colors"
                  rows={3}
                />
              </div>

              <div className="flex gap-3 pt-2">
                <Button
                  onClick={() => {
                    setShowNewProjectModal(false)
                    setNewProjectName("")
                    setNewProjectDescription("")
                  }}
                  variant="outline"
                  className="flex-1 font-mono text-xs uppercase tracking-wider rounded-sm"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateProject}
                  disabled={!newProjectName.trim()}
                  className="flex-1 font-mono text-xs uppercase tracking-wider rounded-sm bg-primary hover:bg-primary/90 disabled:opacity-50"
                >
                  Create Project
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
