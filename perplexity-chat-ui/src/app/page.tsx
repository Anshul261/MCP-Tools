'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { SparklesIcon, MessageSquareIcon, MicIcon, FileIcon } from 'lucide-react'
import ClientOnly from '@/components/ui/client-only'

export default function Home() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-4xl w-full text-center">
        {/* Hero Section */}
        <div className="mb-12">
          <div className="flex items-center justify-center gap-3 mb-6">
            <ClientOnly fallback={<div className="h-12 w-12" />}>
              <SparklesIcon className="h-12 w-12 text-primary" />
            </ClientOnly>
            <h1 className="text-5xl font-bold text-foreground">
              AI Chat Assistant
            </h1>
          </div>
          <p className="text-xl text-foreground-secondary max-w-2xl mx-auto mb-8">
            Your intelligent companion for conversations, research, and productivity. 
            Search online, analyze documents, and get instant answers.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => router.push('/chat')}
              className="text-lg px-8 py-6"
            >
              <ClientOnly fallback={<div className="h-5 w-5 mr-2" />}>
                <MessageSquareIcon className="h-5 w-5 mr-2" />
              </ClientOnly>
              Start Chatting
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => router.push('/auth/login')}
              className="text-lg px-8 py-6"
            >
              Sign In
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="bg-background-secondary p-6 rounded-xl border border-border">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
              <ClientOnly fallback={<div className="h-6 w-6" />}>
                <MessageSquareIcon className="h-6 w-6 text-primary" />
              </ClientOnly>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Smart Conversations
            </h3>
            <p className="text-foreground-secondary">
              Engage in natural conversations with advanced AI models including GPT-4, Claude, and Gemini.
            </p>
          </div>

          <div className="bg-background-secondary p-6 rounded-xl border border-border">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
              <ClientOnly fallback={<div className="h-6 w-6" />}>
                <FileIcon className="h-6 w-6 text-primary" />
              </ClientOnly>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">
              File Analysis
            </h3>
            <p className="text-foreground-secondary">
              Upload and analyze documents, images, and files with AI-powered insights and summaries.
            </p>
          </div>

          <div className="bg-background-secondary p-6 rounded-xl border border-border">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
              <ClientOnly fallback={<div className="h-6 w-6" />}>
                <MicIcon className="h-6 w-6 text-primary" />
              </ClientOnly>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Voice Interactions
            </h3>
            <p className="text-foreground-secondary">
              Communicate naturally with voice messages and audio recordings for hands-free conversations.
            </p>
          </div>
        </div>

        {/* Search Modes */}
        <div className="bg-background-secondary p-8 rounded-xl border border-border">
          <h2 className="text-2xl font-semibold text-foreground mb-6">
            Flexible Search Modes
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-blue-500 font-semibold">🌐</span>
              </div>
              <h3 className="font-medium text-foreground mb-1">Online Search</h3>
              <p className="text-sm text-foreground-secondary">
                Access real-time information from the web
              </p>
            </div>
            <div className="text-center">
              <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-green-500 font-semibold">💾</span>
              </div>
              <h3 className="font-medium text-foreground mb-1">Local Knowledge</h3>
              <p className="text-sm text-foreground-secondary">
                Search through your documents and data
              </p>
            </div>
            <div className="text-center">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-primary font-semibold">🔄</span>
              </div>
              <h3 className="font-medium text-foreground mb-1">Combined Search</h3>
              <p className="text-sm text-foreground-secondary">
                Best of both worlds for comprehensive results
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
