import { Copy, RotateCcw, ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { cn } from "@/lib/utils"
import { Streamdown } from "streamdown"
import { useState } from "react"

interface AnalysisStep {
  type: 'tool_call' | 'agent_switch' | 'progress'
  title: string
  description: string
  timestamp: string
  agent?: string
  tool?: string
}

interface MessageBubbleProps {
  content: string
  isUser: boolean
  timestamp: string
  steps?: AnalysisStep[]
  agentUsed?: string
}

export function MessageBubble({ content, isUser, timestamp, steps, agentUsed }: MessageBubbleProps) {
  const [showSteps, setShowSteps] = useState(false)

  return (
    <div className={cn("flex gap-3 group", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <Avatar className="w-8 h-8 flex-shrink-0 mt-1">
          <AvatarFallback className="bg-accent text-accent-foreground text-xs font-medium">AI</AvatarFallback>
        </Avatar>
      )}

      <div className={cn("max-w-[70%] space-y-2", isUser && "flex flex-col items-end")}>
        <div
          className={cn(
            "rounded-2xl glass border text-pretty shadow-sm",
            isUser
              ? "bg-accent/80 text-accent-foreground border-accent/20 shadow-accent/10"
              : "bg-card/60 text-card-foreground border-border shadow-border/10",
          )}
        >
          <div className="p-4">
            {isUser ? (
              <p className="text-sm leading-relaxed">{content}</p>
            ) : (
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <Streamdown>{content}</Streamdown>
              </div>
            )}
          </div>

          {/* Agent info and steps for AI messages */}
          {!isUser && agentUsed && (
            <div className="border-t border-border/50 px-4 py-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">
                  Analyzed by {agentUsed}
                </span>
                {steps && steps.length > 0 && (
                  <Collapsible open={showSteps} onOpenChange={setShowSteps}>
                    <CollapsibleTrigger asChild>
                      <Button variant="ghost" size="sm" className="h-6 text-xs">
                        {showSteps ? (
                          <>
                            Hide Steps <ChevronUp className="w-3 h-3 ml-1" />
                          </>
                        ) : (
                          <>
                            Show Analysis Steps ({steps.length}) <ChevronDown className="w-3 h-3 ml-1" />
                          </>
                        )}
                      </Button>
                    </CollapsibleTrigger>
                    <CollapsibleContent className="mt-2">
                      <div className="space-y-2 text-xs">
                        {steps.map((step, index) => (
                          <div key={index} className="flex items-start gap-2 p-2 bg-muted/30 rounded">
                            <div className="w-2 h-2 rounded-full bg-accent mt-1 flex-shrink-0" />
                            <div className="flex-1">
                              <div className="font-medium">{step.title}</div>
                              <div className="text-muted-foreground">{step.description}</div>
                              {step.agent && (
                                <div className="text-accent font-medium">Agent: {step.agent}</div>
                              )}
                            </div>
                            <span className="text-muted-foreground text-xs">{step.timestamp}</span>
                          </div>
                        ))}
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <span className="text-xs text-muted-foreground">{timestamp}</span>
          {!isUser && (
            <>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground transition-colors"
              >
                <Copy className="w-3 h-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground transition-colors"
              >
                <RotateCcw className="w-3 h-3" />
              </Button>
            </>
          )}
        </div>
      </div>

      {isUser && (
        <Avatar className="w-8 h-8 flex-shrink-0 mt-1">
          <AvatarImage src="/professional-avatar.png" />
          <AvatarFallback className="bg-secondary text-secondary-foreground text-xs font-medium">You</AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}
