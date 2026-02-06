"use client"

import { useState, useCallback, useRef, type KeyboardEvent, type ChangeEvent } from "react"
import { Send } from "lucide-react"

/* ───── Types ───── */
interface Message {
  role: "user" | "assistant"
  content: string
}
interface TerminalLine {
  text: string
  type: "cmd" | "out"
}

/* ───── Utility ───── */
function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ")
}

/* ───── Sidebar ───── */
function Sidebar({
  selectedModel,
  onModelChange,
  onToggleTerminal,
  terminalVisible,
}: {
  selectedModel: string
  onModelChange: (model: string) => void
  onToggleTerminal: () => void
  terminalVisible: boolean
}) {
  return (
    <aside className="hidden md:flex w-80 shrink-0 flex-col border-r border-border bg-card/70 p-5 backdrop-blur-xl">
      <div className="mb-8">
        <h1 className="bg-gradient-to-r from-primary to-accent bg-clip-text text-2xl font-semibold tracking-tight text-transparent">
          ENGRAM HUB
        </h1>
        <span className="ml-2 rounded-md border border-accent px-1.5 py-0.5 text-xs text-accent">
          v1.2
        </span>
      </div>

      <div className="mb-6">
        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Connectivity
        </p>
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2 rounded-xl border border-border bg-muted/30 px-3 py-2.5 text-sm text-foreground">
            <span className="inline-block h-2 w-2 rounded-full bg-primary shadow-[0_0_10px_hsl(var(--primary))]" />
            Local Engram Model
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-border bg-muted/30 px-3 py-2.5 text-sm text-foreground">
            <span className="inline-block h-2 w-2 rounded-full bg-primary shadow-[0_0_10px_hsl(var(--primary))]" />
            OpenResponses v1
          </div>
        </div>
      </div>

      <div className="mb-6">
        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Model Reasoning
        </p>
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          className="w-full cursor-pointer rounded-xl border border-border bg-muted/30 px-3 py-2.5 font-sans text-sm text-foreground outline-none focus:border-primary"
        >
          <option value="liquid/lfm2.5-1.2b">
            Liquid LFM 2.5 (1.2b) [Local]
          </option>
          <option value="glm-4.7-flash">GLM 4.7 Flash [Remote/Local]</option>
          <option value="custom">{"Custom Engine..."}</option>
        </select>
      </div>

      <div className="mb-6">
        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Neural Fingerprints (Live Context)
        </p>
        <div className="max-h-48 overflow-y-auto">
          <div className="rounded-xl border border-border bg-muted/30 px-3 py-2.5 text-sm text-muted-foreground opacity-50">
            Scanning codebase...
          </div>
        </div>
      </div>

      <div className="mt-auto">
        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          OpenCode Integration
        </p>
        <button
          onClick={onToggleTerminal}
          className="w-full cursor-pointer rounded-xl border border-border bg-muted/30 px-3 py-2.5 text-sm text-foreground transition-colors hover:border-primary"
        >
          {terminalVisible ? "Hide Terminal Console" : "Show Terminal Console"}
        </button>
      </div>
    </aside>
  )
}

/* ───── Chat Messages ───── */
function ChatMessages({
  messages,
  isLoading,
  selectedModel,
}: {
  messages: Message[]
  isLoading: boolean
  selectedModel: string
}) {
  return (
    <div className="flex flex-1 flex-col gap-5 overflow-y-auto p-6 md:p-10">
      {messages.length === 0 && (
        <div className="animate-fade-in rounded-2xl rounded-bl border border-border bg-card/70 px-5 py-4 text-base leading-relaxed backdrop-blur-sm self-start max-w-[80%] text-foreground">
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
              : "self-start rounded-bl-sm border border-border bg-card/70 text-foreground backdrop-blur-sm"
          )}
          dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
        />
      ))}
      {isLoading && (
        <div className="max-w-[80%] animate-fade-in self-start rounded-2xl rounded-bl-sm border border-border bg-card/70 px-5 py-4 italic text-muted-foreground backdrop-blur-sm">
          {"Thinking with "}
          {selectedModel === "liquid/lfm2.5-1.2b" ? "Liquid" : "GLM"}
          {"..."}
        </div>
      )}
    </div>
  )
}

/* ───── Terminal Panel ───── */
function TerminalPanel({
  visible,
  lines,
}: {
  visible: boolean
  lines: TerminalLine[]
}) {
  if (!visible) return null

  return (
    <div className="h-48 overflow-y-auto border-t border-border bg-black p-4 font-mono text-sm">
      {lines.map((line, i) => (
        <div
          key={i}
          className={cn(
            "mb-1",
            line.type === "cmd" ? "text-primary" : "text-muted-foreground"
          )}
        >
          {line.type === "cmd" ? `> ${line.text}` : line.text}
        </div>
      ))}
    </div>
  )
}

/* ───── Chat Input ───── */
function ChatInput({
  value,
  onChange,
  onSend,
  disabled,
}: {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  disabled: boolean
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  function handleInput(e: ChangeEvent<HTMLTextAreaElement>) {
    onChange(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  return (
    <div className="bg-gradient-to-t from-background to-transparent px-6 pb-6 pt-3 md:px-10 md:pb-10 md:pt-5">
      <div className="flex items-center gap-3 rounded-3xl border border-border bg-card/70 px-4 py-2 shadow-[0_10px_40px_rgba(0,0,0,0.4)] backdrop-blur-xl transition-colors focus-within:border-primary">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask about Engram or type /run [cmd]..."
          rows={1}
          className="max-h-36 flex-1 resize-none bg-transparent py-3 font-sans text-base text-foreground outline-none placeholder:text-muted-foreground"
        />
        <button
          onClick={onSend}
          disabled={disabled}
          aria-label="Send message"
          className="flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-full bg-primary text-primary-foreground transition-transform hover:scale-105 hover:bg-accent disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Send className="h-5 w-5" />
        </button>
      </div>
    </div>
  )
}

/* ───── Helpers ───── */
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

/* ───── Main Page ───── */
export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState("liquid/lfm2.5-1.2b")
  const [terminalVisible, setTerminalVisible] = useState(false)
  const [terminalLines, setTerminalLines] = useState<TerminalLine[]>([
    { text: "opencode init --project Engram", type: "cmd" },
    { text: "Project loaded. All files ready for live mutation.", type: "out" },
  ])

  const addTerminalLine = useCallback(
    (text: string, type: "cmd" | "out") => {
      setTerminalLines((prev) => [...prev, { text, type }])
    },
    []
  )

  const handleSend = useCallback(async () => {
    const text = input.trim()
    if (!text || isLoading) return

    setInput("")
    setIsLoading(true)

    const userMessage: Message = { role: "user", content: text }
    setMessages((prev) => [...prev, userMessage])

    if (text.startsWith("/")) {
      const cmd = text.startsWith("/run ") ? text.substring(5) : text.substring(1)
      addTerminalLine(`Executing via OpenCode: ${cmd}`, "cmd")

      try {
        const response = await fetch("/opencode/execute", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ command: cmd }),
        })
        const data = await response.json()
        if (data.error) throw new Error(data.error)

        const output = data.stdout || data.stderr || "Success (no output)"
        addTerminalLine(output, "out")

        const resultMsg = `I have executed the command: \`${cmd}\`\n\n\`\`\`bash\n${output}\n\`\`\``
        setMessages((prev) => [...prev, { role: "assistant", content: resultMsg }])
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Unknown error"
        addTerminalLine(`Error: ${errorMsg}`, "out")
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Failed to execute OpenCode command: ${errorMsg}` },
        ])
      } finally {
        setIsLoading(false)
      }
      return
    }

    const allMessages = [...messages, userMessage]
    try {
      const response = await fetch("/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: selectedModel,
          messages: allMessages,
          max_tokens: 1000,
        }),
      })
      const data = await response.json()
      if (response.ok && data.choices?.[0]) {
        setMessages((prev) => [...prev, { role: "assistant", content: data.choices[0].message.content }])
      } else {
        throw new Error(data.detail || data.error?.message || "Unknown AI server error")
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error"
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `**Connection Error:** ${errorMsg}\n\nTroubleshooting:\n1. Is **${selectedModel}** loaded in LM Studio?\n2. Is the LM Studio server running on port 1234?\n3. Try switching the model in the sidebar.`,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }, [input, isLoading, messages, selectedModel, addTerminalLine])

  return (
    <div className="flex h-dvh overflow-hidden">
      <Sidebar
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        onToggleTerminal={() => setTerminalVisible((v) => !v)}
        terminalVisible={terminalVisible}
      />

      <main className="flex flex-1 flex-col">
        <ChatMessages
          messages={messages}
          isLoading={isLoading}
          selectedModel={selectedModel}
        />
        <TerminalPanel visible={terminalVisible} lines={terminalLines} />
        <ChatInput
          value={input}
          onChange={setInput}
          onSend={handleSend}
          disabled={isLoading}
        />
      </main>
    </div>
  )
}
