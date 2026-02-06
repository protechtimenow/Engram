"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { Send, Bot, User, Power, ArrowLeft } from "lucide-react"
import Link from "next/link"

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ")
}

interface Message {
  role: "user" | "assistant" | "system"
  content: string
  timestamp?: string
}

const WS_URL = "ws://localhost:17500"
const AUTH_TOKEN = "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"

export default function ClawdBotPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState("Disconnected")
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isConnectingRef = useRef(false)
  const intentionalCloseRef = useRef(false)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const addSystemMessage = useCallback((content: string) => {
    setMessages((prev) => [
      ...prev,
      { role: "system", content, timestamp: new Date().toLocaleTimeString() },
    ])
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || isConnectingRef.current) {
      return
    }

    isConnectingRef.current = true
    intentionalCloseRef.current = false
    setIsConnecting(true)
    setConnectionStatus("Connecting...")

    try {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        setIsConnecting(false)
        isConnectingRef.current = false
        setConnectionStatus("Connected")
        addSystemMessage("Connected to ClawdBot gateway")
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === "event" && data.event === "connect.challenge") {
            const authMsg = {
              type: "req",
              id: crypto.randomUUID(),
              method: "connect",
              params: {
                minProtocol: 3,
                maxProtocol: 3,
                client: {
                  id: "engram-web-client",
                  displayName: "Engram Web Hub",
                  version: "1.0.0",
                  platform: "web",
                  mode: "frontend",
                },
                caps: ["chat"],
                auth: { token: AUTH_TOKEN },
                role: "operator",
                scopes: ["operator.admin"],
              },
            }
            ws.send(JSON.stringify(authMsg))
          } else if (data.type === "res" && data.ok === true) {
            addSystemMessage("Authentication successful")
          } else if (data.type === "res" && data.ok === false) {
            addSystemMessage(
              `Authentication failed: ${data.error?.message || "Unknown error"}`
            )
          } else if (data.type === "ping") {
            ws.send(
              JSON.stringify({
                type: "pong",
                data: data.data,
                timestamp: new Date().toISOString(),
              })
            )
          } else if (data.type === "req" && data.method === "chat.send") {
            const content = data.params?.message || ""
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content,
                timestamp: new Date().toLocaleTimeString(),
              },
            ])
            // Acknowledge the request
            ws.send(
              JSON.stringify({ type: "res", id: data.id, ok: true, result: {} })
            )
          }
        } catch {
          // Ignore malformed messages
        }
      }

      ws.onerror = () => {
        setConnectionStatus("Error")
        setIsConnecting(false)
        isConnectingRef.current = false
      }

      ws.onclose = () => {
        setIsConnected(false)
        setIsConnecting(false)
        isConnectingRef.current = false
        setConnectionStatus("Disconnected")
        wsRef.current = null
        if (!intentionalCloseRef.current) {
          addSystemMessage("Disconnected from ClawdBot")
        }
      }
    } catch {
      setIsConnecting(false)
      isConnectingRef.current = false
      setConnectionStatus("Error")
      addSystemMessage("Failed to create WebSocket connection")
    }
  }, [addSystemMessage])

  const disconnect = useCallback(() => {
    intentionalCloseRef.current = true
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    addSystemMessage("Disconnected from ClawdBot")
  }, [addSystemMessage])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      intentionalCloseRef.current = true
      wsRef.current?.close()
    }
  }, [])

  const sendMessage = useCallback(() => {
    if (!input.trim() || !isConnected || !wsRef.current) return

    const message = input.trim()
    setInput("")

    setMessages((prev) => [
      ...prev,
      { role: "user", content: message, timestamp: new Date().toLocaleTimeString() },
    ])

    const chatMsg = {
      type: "req",
      id: crypto.randomUUID(),
      method: "chat.send",
      params: {
        message,
        context: { source: "web", timestamp: new Date().toISOString() },
      },
    }

    wsRef.current.send(JSON.stringify(chatMsg))
  }, [input, isConnected])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex h-dvh flex-col bg-background text-foreground">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-card/70 px-4 py-3 backdrop-blur-xl md:px-6 md:py-4">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-border text-muted-foreground transition-colors hover:border-primary hover:text-primary"
            aria-label="Back to Engram Hub"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <Bot className="h-6 w-6 text-primary" />
          <h1 className="text-lg font-semibold md:text-xl">ClawdBot</h1>
          <span className="hidden rounded-md border border-border bg-muted/30 px-2 py-0.5 text-xs text-muted-foreground sm:inline-block">
            {WS_URL}
          </span>
        </div>
        <div className="flex items-center gap-3 md:gap-4">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "h-2 w-2 rounded-full",
                isConnected && "bg-[hsl(142,71%,45%)] shadow-[0_0_10px_hsl(142,71%,45%)]",
                isConnecting && "animate-pulse bg-[hsl(48,96%,53%)]",
                !isConnected && !isConnecting && "bg-destructive"
              )}
            />
            <span className="hidden text-sm text-muted-foreground sm:inline">
              {connectionStatus}
            </span>
          </div>
          <button
            onClick={isConnected ? disconnect : connect}
            disabled={isConnecting}
            className={cn(
              "flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition-colors md:px-4",
              isConnected
                ? "border border-destructive/30 bg-destructive/10 text-destructive hover:bg-destructive/20"
                : "border border-primary/30 bg-primary/10 text-primary hover:bg-primary/20",
              isConnecting && "cursor-not-allowed opacity-50"
            )}
          >
            <Power className="h-4 w-4" />
            <span className="hidden sm:inline">
              {isConnecting ? "Connecting..." : isConnected ? "Disconnect" : "Connect"}
            </span>
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-4 text-muted-foreground">
            <Bot className="h-16 w-16 opacity-20" />
            <p className="text-lg">Connect to ClawdBot to start chatting</p>
            <p className="text-sm">Click the Connect button above</p>
          </div>
        )}

        <div className="mx-auto max-w-4xl space-y-3">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "animate-fade-in flex gap-3 rounded-2xl p-4",
                msg.role === "user" &&
                  "ml-8 bg-gradient-to-br from-primary/15 to-accent/10 md:ml-16",
                msg.role === "assistant" &&
                  "mr-8 border border-primary/20 bg-card/70 backdrop-blur-sm md:mr-16",
                msg.role === "system" &&
                  "mx-8 justify-center bg-muted/20 text-center text-sm text-muted-foreground md:mx-16"
              )}
            >
              {msg.role !== "system" && (
                <div
                  className={cn(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                    msg.role === "user" ? "bg-muted" : "bg-primary/15"
                  )}
                >
                  {msg.role === "user" ? (
                    <User className="h-4 w-4 text-foreground" />
                  ) : (
                    <Bot className="h-4 w-4 text-primary" />
                  )}
                </div>
              )}
              <div className="flex-1">
                {msg.role !== "system" && (
                  <div className="mb-1 flex items-center gap-2">
                    <span
                      className={cn(
                        "text-sm font-medium",
                        msg.role === "user" ? "text-foreground" : "text-primary"
                      )}
                    >
                      {msg.role === "user" ? "You" : "ClawdBot"}
                    </span>
                    {msg.timestamp && (
                      <span className="text-xs text-muted-foreground">
                        {msg.timestamp}
                      </span>
                    )}
                  </div>
                )}
                <p className="whitespace-pre-wrap leading-relaxed text-foreground">
                  {msg.content}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-border bg-card/70 p-3 backdrop-blur-xl md:p-4">
        <div className="mx-auto flex max-w-4xl gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isConnected
                ? "Type a message..."
                : "Connect first to send messages"
            }
            disabled={!isConnected}
            className="flex-1 rounded-xl border border-border bg-muted/30 px-4 py-3 text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-primary disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={!isConnected || !input.trim()}
            aria-label="Send message"
            className="flex items-center gap-2 rounded-xl bg-primary px-4 py-3 font-medium text-primary-foreground transition-transform hover:scale-105 hover:bg-accent disabled:cursor-not-allowed disabled:opacity-50 md:px-6"
          >
            <Send className="h-4 w-4" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
      </div>
    </div>
  )
}
