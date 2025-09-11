import { Copy, RotateCcw, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

interface Visualization {
  filename: string
  url: string
  type: "html" | "image"
  created: number
}

interface MessageBubbleProps {
  content: string
  isUser: boolean
  timestamp: string
  visualizations?: Visualization[]
}

export function MessageBubble({ content, isUser, timestamp, visualizations = [] }: MessageBubbleProps) {
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
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
          
          {/* Display visualizations */}
          {!isUser && visualizations.length > 0 && (
            <div className="mt-4 space-y-3">
              {visualizations.map((viz, index) => (
                <div key={index} className="border rounded-lg p-3 bg-background/50">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-muted-foreground">
                      {viz.type === 'image' ? '📊 Chart' : '📈 Interactive Dashboard'}
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
                    <div className="bg-muted/30 rounded p-4 text-center">
                      <p className="text-sm text-muted-foreground mb-2">Interactive Dashboard</p>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => window.open(`http://localhost:7777${viz.url}`, '_blank')}
                      >
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
