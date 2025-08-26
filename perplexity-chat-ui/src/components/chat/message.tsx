'use client'

import { useState } from 'react'
import { Message as MessageType, ChainOfThoughtEvent } from '@/types'
import { formatDate, cn } from '@/lib/utils'
import { UserIcon, BotIcon, ChevronDownIcon, ChevronRightIcon, ClockIcon, WrenchIcon, BrainIcon, MessageSquareIcon, FileTextIcon, GlobeIcon } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { motion, AnimatePresence } from 'framer-motion'
import 'highlight.js/styles/github-dark.css'

interface MessageProps {
  message: MessageType
}


export default function Message({ message }: MessageProps) {
  const isUser = message.role === 'user'
  const [showChainOfThought, setShowChainOfThought] = useState(true) // Show chain of thought by default
  const hasChainOfThought = message.chainOfThought && message.chainOfThought.length > 0

  const getEventIcon = (event: ChainOfThoughtEvent) => {
    if (event.type === 'tool_call') return <WrenchIcon className="h-3 w-3" />
    if (event.type === 'memory_update') return <BrainIcon className="h-3 w-3" />
    if (event.event?.includes('Started')) return <ClockIcon className="h-3 w-3" />
    return <div className="w-3 h-3 rounded-full bg-primary/20" />
  }

  const getEventDescription = (event: ChainOfThoughtEvent) => {
    if (event.tool) {
      return `${event.agent_name || 'Agent'} used ${event.tool}${event.duration ? ` (${event.duration})` : ''}`
    }
    if (event.event?.includes('Started')) {
      return `${event.agent_name || event.event} started processing`
    }
    if (event.event?.includes('Memory')) {
      return `${event.agent_name || 'Agent'} updated memory`
    }
    if (event.event?.includes('Content')) {
      return `${event.agent_name || 'Agent'} generated response`
    }
    return event.raw?.substring(0, 80) + '...'
  }

  return (
    <div className={cn(
      "flex gap-4 p-6 border-b border-border/50",
      isUser ? "bg-background" : "bg-background-secondary/30"
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser 
          ? "bg-primary text-white" 
          : "bg-accent text-foreground"
      )}>
        {isUser ? (
          <UserIcon className="h-4 w-4" />
        ) : (
          <BotIcon className="h-4 w-4" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <span className="font-medium text-foreground">
            {isUser ? 'You' : 'Assistant'}
          </span>
          <span className="text-xs text-foreground-muted">
            {message.timestamp ? formatDate(message.timestamp) : 'Now'}
          </span>
        </div>

        {/* Chain of Thought - Show First */}
        {hasChainOfThought && (
          <div className="mb-4">
            <motion.button
              onClick={() => setShowChainOfThought(!showChainOfThought)}
              className="flex items-center gap-2 text-sm text-foreground-muted hover:text-foreground transition-colors mb-3"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {showChainOfThought ? (
                <ChevronDownIcon className="h-4 w-4" />
              ) : (
                <ChevronRightIcon className="h-4 w-4" />
              )}
              <span>
                Agent reasoning steps ({message.chainOfThought?.length || 0} events)
              </span>
            </motion.button>

            <AnimatePresence>
              {showChainOfThought && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="border border-border/30 rounded-lg bg-background-secondary/20 mb-4"
                >
                  <div className="p-3 border-b border-border/20 bg-background-secondary/30">
                    <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
                      <BrainIcon className="h-4 w-4" />
                      Chain of Thought
                    </h4>
                    <p className="text-xs text-foreground-muted">Real-time agent reasoning and execution</p>
                  </div>
                  
                  <div className="p-3 space-y-3 max-h-96 overflow-y-auto">
                    {message.chainOfThought?.map((event, index) => {
                      const isToolCall = event.raw?.includes('ToolCallStarted') || event.raw?.includes('completed in')
                      const isAgentEvent = event.raw?.includes('RunResponseStarted') || event.raw?.includes('RunResponseContent')
                      const agentName = event.agent_id === 'doc_agent' ? 'Document Agent' : 
                                      event.agent_id === 'web_agent' ? 'Web Agent' : 
                                      event.agent_id || 'Team'
                      
                      return (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.1, delay: index * 0.02 }}
                          className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
                            isToolCall ? 'bg-blue-50 dark:bg-blue-950/30 border-l-4 border-blue-400' :
                            isAgentEvent ? 'bg-emerald-50 dark:bg-emerald-950/30 border-l-4 border-emerald-400' :
                            'bg-background/50 hover:bg-background/70'
                          }`}
                        >
                          <div className="mt-1 flex-shrink-0">
                            {event.agent_id === 'doc_agent' && <FileTextIcon className="h-4 w-4 text-emerald-500" />}
                            {event.agent_id === 'web_agent' && <GlobeIcon className="h-4 w-4 text-blue-500" />}
                            {!event.agent_id && getEventIcon(event)}
                          </div>
                          <div className="flex-1 min-w-0 space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-medium text-foreground-muted uppercase tracking-wide">
                                {agentName}
                              </span>
                              {event.timestamp && (
                                <span className="text-xs text-foreground-muted">
                                  {new Date(event.timestamp).toLocaleTimeString()}
                                </span>
                              )}
                            </div>
                            <div className="text-sm text-foreground">
                              {isToolCall && event.raw?.includes('completed in') ? (
                                <div className="flex items-center gap-2">
                                  <WrenchIcon className="h-3 w-3 text-green-500" />
                                  <span className="font-medium">{event.raw.split('(')[0]} completed</span>
                                  <span className="text-foreground-muted">{event.raw.match(/completed in ([0-9.]+s)/)?.[1]}</span>
                                </div>
                              ) : isToolCall ? (
                                <div className="flex items-center gap-2">
                                  <ClockIcon className="h-3 w-3 text-blue-500" />
                                  <span>Tool call started: {event.raw?.match(/tool_name='([^']+)'/)?.[1] || 'Unknown'}</span>
                                </div>
                              ) : isAgentEvent ? (
                                <div className="flex items-center gap-2">
                                  <BrainIcon className="h-3 w-3 text-emerald-500" />
                                  <span>{event.event?.includes('Started') ? 'Agent started processing' : 'Generating response'}</span>
                                </div>
                              ) : (
                                <details className="cursor-pointer">
                                  <summary className="text-foreground-muted hover:text-foreground">
                                    Raw event data
                                  </summary>
                                  <pre className="text-xs text-foreground-muted mt-2 p-2 bg-muted rounded overflow-x-auto font-mono">
                                    {event.raw}
                                  </pre>
                                </details>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      )
                    })}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Agent Response Content */}
        {message.content && (
          <div className="max-w-none">
            <div className="border-l-4 border-primary/30 pl-4">
              <h4 className="text-sm font-medium text-primary mb-2 flex items-center gap-2">
                <MessageSquareIcon className="h-4 w-4" />
                Agent Response
              </h4>
              <div className="space-y-4">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight]}
                  components={{
                    // Headers with better spacing and styling
                    h1: ({ children }) => (
                      <h1 className="text-2xl font-bold text-foreground mt-8 mb-4 pb-2 border-b-2 border-primary/20">
                        {children}
                      </h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-xl font-bold text-foreground mt-6 mb-3 pb-2 border-b border-border/30">
                        {children}
                      </h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-lg font-semibold text-foreground mt-5 mb-3 flex items-center gap-2">
                        {children?.toString()?.includes('Document Agent') && <FileTextIcon className="h-4 w-4 text-emerald-500" />}
                        {children?.toString()?.includes('Web Agent') && <GlobeIcon className="h-4 w-4 text-blue-500" />}
                        {children?.toString()?.includes('Final Team') && <BrainIcon className="h-4 w-4 text-purple-500" />}
                        {children}
                      </h3>
                    ),
                    h4: ({ children }) => (
                      <h4 className="text-base font-semibold text-foreground mt-4 mb-2">
                        {children}
                      </h4>
                    ),
                    h5: ({ children }) => (
                      <h5 className="text-sm font-semibold text-foreground mt-3 mb-2">
                        {children}
                      </h5>
                    ),
                    h6: ({ children }) => (
                      <h6 className="text-sm font-medium text-foreground/80 mt-2 mb-2">
                        {children}
                      </h6>
                    ),
                    
                    // Paragraphs with proper spacing
                    p: ({ children }) => (
                      <p className="text-foreground leading-7 mb-4 [&:not(:first-child)]:mt-4">
                        {children}
                      </p>
                    ),
                    
                    // Lists with better styling
                    ul: ({ children }) => (
                      <ul className="list-disc pl-6 mb-4 space-y-2 text-foreground">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal pl-6 mb-4 space-y-2 text-foreground">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li className="text-foreground leading-7">
                        {children}
                      </li>
                    ),
                    
                    // Enhanced table styling
                    table: ({ children }) => (
                      <div className="overflow-x-auto my-6 rounded-lg border border-border shadow-sm">
                        <table className="w-full border-collapse bg-background">
                          {children}
                        </table>
                      </div>
                    ),
                    thead: ({ children }) => (
                      <thead className="bg-muted/50">
                        {children}
                      </thead>
                    ),
                    tbody: ({ children }) => (
                      <tbody className="divide-y divide-border">
                        {children}
                      </tbody>
                    ),
                    th: ({ children }) => (
                      <th className="px-4 py-3 text-left text-sm font-semibold text-foreground border-b border-border">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="px-4 py-3 text-sm text-foreground">
                        {children}
                      </td>
                    ),
                    
                    // Better horizontal rules
                    hr: () => <hr className="border-border/40 my-6" />,
                    
                    // Enhanced blockquotes
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-primary/40 pl-4 py-2 italic text-foreground/90 bg-muted/20 rounded-r-lg my-4">
                        {children}
                      </blockquote>
                    ),
                    
                    // Better links
                    a: ({ href, children }) => (
                      <a 
                        href={href} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-primary hover:text-primary/80 underline decoration-primary/30 hover:decoration-primary/60 transition-colors inline-flex items-center gap-1 font-medium"
                      >
                        {children}
                        <svg className="h-3 w-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    ),
                    
                    // Enhanced code blocks
                    code: ({ inline, children, className }: any) => {
                      const language = className?.replace('language-', '') || ''
                      return inline ? (
                        <code className="bg-muted/60 px-1.5 py-0.5 rounded text-foreground font-mono text-sm border">
                          {children}
                        </code>
                      ) : (
                        <div className="relative my-4">
                          {language && (
                            <div className="absolute top-0 right-0 bg-muted/80 px-2 py-1 text-xs font-medium text-foreground/70 rounded-bl-md rounded-tr-lg border border-border">
                              {language}
                            </div>
                          )}
                          <pre className="bg-muted/40 border border-border p-4 rounded-lg font-mono text-sm overflow-x-auto">
                            <code className="text-foreground">
                              {children}
                            </code>
                          </pre>
                        </div>
                      )
                    },
                    
                    // Enhanced strong and em
                    strong: ({ children }) => (
                      <strong className="font-semibold text-foreground">
                        {children}
                      </strong>
                    ),
                    em: ({ children }) => (
                      <em className="italic text-foreground/90">
                        {children}
                      </em>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        )}

        {/* Legacy Chain of Thought Toggle (hidden) */}
        {/* This section was moved above */}

      </div>
    </div>
  )
}