import type { Message } from "@/lib/types";
import { cn } from "@/lib/utils";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold flex-shrink-0">
          AI
        </div>
      )}
      <div
        className={cn(
          "max-w-[70%] rounded-lg px-3 py-2 text-sm",
          isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-foreground",
          message.contains_injected_fact && "ring-1 ring-yellow-400/60"
        )}
      >
        <p>{message.content}</p>
        {message.contains_injected_fact && (
          <p className="text-xs opacity-60 mt-1">Fact injected at turn {message.turn_number}</p>
        )}
      </div>
    </div>
  );
}
