"use client"

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ")
}

export interface Message {
  role: "user" | "assistant"
  content: string
}

interface ChatMessagesProps {
  messages: Message[]
  isLoading: boolean
  selectedModel: string
}

export function ChatMessages({
  messages,
  isLoading,
  selectedModel,
}: ChatMessagesProps) {
  return (
    <div className="flex flex-1 flex-col gap-5 overflow-y-auto p-10">
      {messages.length === 0 && (
        <div className="animate-fade-in rounded-2xl rounded-bl border border-border bg-card/70 px-5 py-4 text-base leading-relaxed backdrop-blur-sm self-start max-w-[80%]">
          Hello. I am strictly wired to the <strong>Engram</strong> project
          context. I can see your architecture specs and n-gram hashing logic.
          How shall we advance the codebase today?
        </div>
      )}
      {messages.map((msg, i) => (
        <div
          key={i}
          className={cn(
            "max-w-[80%] animate-fade-in rounded-2xl px-5 py-4 text-base leading-relaxed",
            msg.role === "user"
              ? "self-end rounded-br-sm bg-gradient-to-br from-primary to-accent font-medium text-primary-foreground"
              : "self-start rounded-bl-sm border border-border bg-card/70 backdrop-blur-sm"
          )}
          dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
        />
      ))}
      {isLoading && (
        <div className="max-w-[80%] animate-fade-in self-start rounded-2xl rounded-bl-sm border border-border bg-card/70 px-5 py-4 italic text-muted-foreground backdrop-blur-sm">
          Thinking with{" "}
          {selectedModel === "liquid/lfm2.5-1.2b" ? "Liquid" : "GLM"}...
        </div>
      )}
    </div>
  )
}

function formatContent(content: string): string {
  return content
    .replace(/```(\w*)\n([\s\S]*?)```/g, (_match, _lang, code) => {
      return `<pre class="my-2 overflow-x-auto rounded-lg border border-[hsl(var(--border))] bg-black/30 p-3"><code class="font-mono text-sm">${escapeHtml(code)}</code></pre>`
    })
    .replace(
      /`([^`]+)`/g,
      '<code class="rounded bg-white/10 px-1.5 py-0.5 font-mono text-sm">$1</code>'
    )
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br/>")
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
}
