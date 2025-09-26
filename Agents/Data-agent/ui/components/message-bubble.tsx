import { Copy, RotateCcw, ExternalLink, Bot, BarChart3, TrendingUp, PieChart, LayoutDashboard } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { Streamdown } from "streamdown"

interface Visualization {
  filename: string
  url: string
  type: "html" | "image"
  created: number
}

interface AnalysisStep {
  type: 'tool_call' | 'agent_switch' | 'progress' | 'visualization'
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
  visualizations?: Visualization[]
  agentUsed?: string
  steps?: AnalysisStep[]
  visualizationMode?: 'dashboard' | 'single_chart' | null
}

export function MessageBubble({ content, isUser, timestamp, visualizations = [], agentUsed, steps = [], visualizationMode }: MessageBubbleProps) {
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
            "p-4 rounded-2xl glass border text-pretty shadow-sm",
            isUser
              ? "bg-accent/80 text-accent-foreground border-accent/20 shadow-accent/10"
              : "bg-card/60 text-card-foreground border-border shadow-border/10",
          )}
        >
          <div className="text-sm leading-relaxed prose prose-sm max-w-none prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-code:text-foreground prose-pre:bg-muted prose-pre:border prose-pre:border-border">
            <Streamdown>{content}</Streamdown>
          </div>

          {/* Display agent info with visualization mode */}
          {!isUser && agentUsed && (
            <div className="mt-2 flex items-center justify-between">
              <div className="text-xs text-muted-foreground">
                <Bot className="w-3 h-3 inline mr-1" />{agentUsed}
              </div>
              {visualizationMode && (
                <div className={cn("text-xs px-2 py-1 rounded-full",
                  visualizationMode === 'dashboard' ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700"
                )}>
                  {visualizationMode === 'dashboard' ? (
                    <><LayoutDashboard className="w-3 h-3 inline mr-1" />Dashboard Mode</>
                  ) : (
                    <><PieChart className="w-3 h-3 inline mr-1" />Single Chart</>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Display analysis steps */}
          {!isUser && steps && steps.length > 0 && (
            <div className="mt-3 border-t border-border/50 pt-3">
              <div className="text-xs font-medium text-muted-foreground mb-2">Analysis Steps:</div>
              <div className="space-y-1">
                {steps.map((step, index) => (
                  <div key={index} className="flex items-start gap-2 text-xs">
                    <div className={cn(
                      "w-2 h-2 rounded-full mt-1 flex-shrink-0",
                      step.type === 'tool_call' ? "bg-blue-400" :
                      step.type === 'agent_switch' ? "bg-green-400" : "bg-gray-400"
                    )} />
                    <div className="flex-1">
                      <div className="text-foreground">{step.title}</div>
                      {step.description && (
                        <div className="text-muted-foreground text-[10px] mt-0.5">{step.description}</div>
                      )}
                      {step.agent && (
                        <div className="text-accent text-[10px]">Agent: {step.agent}</div>
                      )}
                    </div>
                    <div className="text-muted-foreground text-[10px] whitespace-nowrap">{step.timestamp}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Display visualizations */}
          {!isUser && visualizations.length > 0 && (
            <div className="mt-4 space-y-3">
              {visualizations.map((viz, index) => (
                <div key={index} className="border rounded-lg p-3 bg-background/50">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-muted-foreground">
                      {viz.type === 'image' ? <><BarChart3 className="w-3 h-3 inline mr-1" />Chart</> : <><TrendingUp className="w-3 h-3 inline mr-1" />Interactive Dashboard • Multiple Charts</>}
                    </span>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 w-6 p-0"
                      onClick={() => window.open(`http://localhost:7777${viz.url}`, '_blank')}
                    >
                      <ExternalLink className="w-3 h-3" />
                    </Button>
                  </div>
                  
                  {viz.type === 'image' ? (
                    <img 
                      src={`http://localhost:7777${viz.url}`}
                      alt={viz.filename}
                      className="w-full h-auto rounded border"
                      onError={(e) => {
                        console.error('Image load error:', e);
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  ) : (
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded p-4 text-center border-2 border-dashed border-blue-200">
                      <LayoutDashboard className="w-8 h-8 mx-auto mb-2 text-blue-500" />
                      <p className="text-sm font-medium text-blue-700 mb-2">Multi-Chart Dashboard</p>
                      <p className="text-xs text-blue-600 mb-3">Interactive charts with data insights</p>
                      <Button
                        variant="outline"
                        size="sm"
                        className="border-blue-300 text-blue-700 hover:bg-blue-100"
                        onClick={() => window.open(`http://localhost:7777${viz.url}`, '_blank')}
                      >
                        <ExternalLink className="w-3 h-3 mr-1" />
                        Open Dashboard
                      </Button>
                    </div>
                  )}
                </div>
              ))}
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
