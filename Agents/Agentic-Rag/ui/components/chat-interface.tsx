"use client"

import { useState } from "react"
import { Sidebar } from "./sidebar"
import { ChatArea } from "./chat-area"

export function ChatInterface() {
  const [selectedChat, setSelectedChat] = useState("Data Explorer")

  return (
    <div className="flex h-screen w-full bg-gradient-to-br from-background via-background to-slate-900/50">
      <Sidebar selectedChat={selectedChat} onSelectChat={setSelectedChat} />
      <ChatArea selectedChat={selectedChat} />
    </div>
  )
}
