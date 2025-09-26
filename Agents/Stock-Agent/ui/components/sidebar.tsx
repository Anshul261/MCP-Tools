"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Search, Plus, ChevronDown, ChevronRight, Folder, MessageSquare, Settings, Sun } from "lucide-react"
import { cn } from "@/lib/utils"

interface SidebarProps {
  selectedChat: string
  onSelectChat: (chat: string) => void
}

export function Sidebar({ selectedChat, onSelectChat }: SidebarProps) {
  const [expandedFolders, setExpandedFolders] = useState<string[]>(["AgentOS"])

  const toggleFolder = (folder: string) => {
    setExpandedFolders((prev) => (prev.includes(folder) ? prev.filter((f) => f !== folder) : [...prev, folder]))
  }

  const folders = [
    {
      name: "AgentOS",
      items: ["Stock Analysis", "Team Manager", "Agent Status"],
    },
    {
      name: "Work",
      items: ["Marketing Plan", "Competitor Analysis", "Q2 Strategy"],
    },
    {
      name: "Personal",
      items: ["Daily Journal", "Coding Help", "Travel Itinerary"],
    },
  ]

  const chats = ["Stock Analysis", "General Chat", "Investment Ideas", "Market News", "Portfolio Review"]

  return (
    <div className="w-80 h-full glass-strong bg-sidebar/80 border-r border-sidebar-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
            <Sun className="w-4 h-4 text-accent-foreground" />
          </div>
          <h1 className="font-semibold text-white">Stock AgentOS</h1>
        </div>

        <Button
          className="w-full glass bg-card/50 hover:bg-card/70 border border-border text-white hover:text-white"
          variant="outline"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Chat
        </Button>
      </div>

      {/* Search */}
      <div className="p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search Chats"
            className="pl-10 glass bg-input/50 border-border text-white placeholder:text-muted-foreground"
          />
          <kbd className="absolute right-3 top-1/2 transform -translate-y-1/2 px-2 py-1 text-xs bg-accent/30 rounded border border-accent/50 text-white font-medium">
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Folders */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 pb-2">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Folders</h3>

          {folders.map((folder) => (
            <div key={folder.name} className="mb-2">
              <Button
                variant="ghost"
                className="w-full justify-start p-2 h-auto glass hover:bg-card/30 text-white hover:text-white"
                onClick={() => toggleFolder(folder.name)}
              >
                <Folder className="w-4 h-4 mr-2 text-accent" />
                <span className="flex-1 text-left">{folder.name}</span>
                {expandedFolders.includes(folder.name) ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </Button>

              {expandedFolders.includes(folder.name) && (
                <div className="ml-6 mt-1 space-y-1">
                  {folder.items.map((item) => (
                    <Button
                      key={item}
                      variant="ghost"
                      className={cn(
                        "w-full justify-start p-2 h-auto text-sm glass hover:bg-card/30 text-white hover:text-white transition-all duration-200",
                        selectedChat === item &&
                          "bg-accent/30 text-white border border-accent/50 shadow-lg shadow-accent/20",
                      )}
                      onClick={() => onSelectChat(item)}
                    >
                      {item}
                    </Button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Chats */}
        <div className="px-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Chats</h3>

          {chats.map((chat) => (
            <Button
              key={chat}
              variant="ghost"
              className={cn(
                "w-full justify-start p-2 h-auto mb-1 glass hover:bg-card/30 text-white hover:text-white transition-all duration-200",
                selectedChat === chat && "bg-accent/30 text-white border border-accent/50 shadow-lg shadow-accent/20",
              )}
              onClick={() => onSelectChat(chat)}
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              {chat}
            </Button>
          ))}
        </div>
      </div>

      {/* User Profile */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="flex items-center gap-3">
          <Avatar className="w-8 h-8">
            <AvatarImage src="/professional-avatar.png" />
            <AvatarFallback className="bg-accent text-accent-foreground">AW</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-sidebar-foreground truncate">Augustas Web</p>
            <p className="text-xs text-muted-foreground truncate">augustasarmalis@gmail.com</p>
          </div>
          <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
