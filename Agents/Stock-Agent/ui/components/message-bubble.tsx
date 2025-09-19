import { Copy, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

interface MessageBubbleProps {
  content: string
  isUser: boolean
  timestamp: string
}

export function MessageBubble({ content, isUser, timestamp }: MessageBubbleProps) {
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
          <p className="text-sm leading-relaxed">{content}</p>
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
