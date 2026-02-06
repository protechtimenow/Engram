"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { Send, Bot, User, Power } from "lucide-react"

interface Message {
  role: "user" | "assistant" | "system"
  content: string
  timestamp?: string
}

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ")
}

export default function ClawdBotPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState("Disconnected")
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isConnectingRef = useRef(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const connect = useCallback(() => {
    // Prevent multiple concurrent connection attempts
    if (isConnectingRef.current) {
      console.log("Already connecting, skipping...")
      return
    }
    
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      console.log("WebSocket already open or connecting, skipping...")
      return
    }

    isConnectingRef.current = true
    setIsConnecting(true)
    setConnectionStatus("Connecting...")

    console.log("Creating new WebSocket connection...")
    const ws = new WebSocket("ws://localhost:17500")
    
    ws.onopen = () => {
      console.log("WebSocket opened")
      // Don't set connected yet - wait for authentication
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log("Received:", data)

        if (data.type === "event" && data.event === "connect.challenge") {
          console.log("Got auth challenge, sending auth...")
          // Send authentication
          const authMsg = {
            type: "req",
            id: Math.random().toString(36).substring(2) + Date.now().toString(36),
            method: "connect",
            params: {
              minProtocol: 3,
              maxProtocol: 3,
              client: {
                id: "gateway-client",
                displayName: "Engram Web Hub",
                version: "1.0.0",
                platform: "python",
                mode: "backend"
              },
              caps: ["chat"],
              auth: {
                token: "2a965e2334ac2b0a9d4d255f86e479db5a3b75a992affbdc"
              },
              role: "operator",
              scopes: ["operator.admin"]
            }
          }
          ws.send(JSON.stringify(authMsg))
        } else if (data.type === "res" && data.ok === true) {
          console.log("Authentication successful")
          setIsConnected(true)
          setIsConnecting(false)
          isConnectingRef.current = false
          setConnectionStatus("Connected")
          setMessages(prev => [...prev, {
            role: "system",
            content: "Connected and authenticated to ClawdBot",
            timestamp: new Date().toLocaleTimeString()
          }])
        } else if (data.type === "res" && data.ok === false) {
          console.error("Authentication failed:", JSON.stringify(data, null, 2))
          setConnectionStatus("Auth Failed")
          setIsConnecting(false)
          isConnectingRef.current = false
          setMessages(prev => [...prev, {
            role: "system",
            content: `Authentication failed: ${data.error?.message || "Unknown error"}`,
            timestamp: new Date().toLocaleTimeString()
          }])
          ws.close()
        } else if (data.type === "ping") {
          // Send pong
          ws.send(JSON.stringify({
            type: "pong",
            data: data.data,
            timestamp: new Date().toISOString()
          }))
        } else if (data.type === "res" && data.ok === true && data.payload) {
          // Received response from bot
          const content = data.payload.message || data.payload.content || ""
          if (content) {
            setMessages(prev => [...prev, {
              role: "assistant",
              content: content,
              timestamp: new Date().toLocaleTimeString()
            }])
          }
        } else if (data.type === "event") {
          // Handle other events
          console.log("Event received:", data.event)
        }
      } catch (err) {
        console.error("Error parsing message:", err)
      }
    }

    ws.onerror = (error) => {
      console.error("WebSocket error:", error)
      setConnectionStatus("Error")
      setIsConnecting(false)
      isConnectingRef.current = false
    }

    ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason)
      setIsConnected(false)
      setIsConnecting(false)
      isConnectingRef.current = false
      setConnectionStatus("Disconnected")
      
      // Only add disconnect message if we were previously connected
      if (wsRef.current) {
        setMessages(prev => [...prev, {
          role: "system",
          content: `Disconnected from ClawdBot (code: ${event.code})`,
          timestamp: new Date().toLocaleTimeString()
        }])
      }
      
      wsRef.current = null
    }

    wsRef.current = ws
  }, [])

  const disconnect = useCallback(() => {
    console.log("Disconnecting...")
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    wsRef.current?.close()
    wsRef.current = null
    isConnectingRef.current = false
  }, [])

  const sendMessage = useCallback(() => {
    if (!input.trim() || !isConnected || !wsRef.current) return

    const message = input.trim()
    setInput("")

    // Add user message to UI
    setMessages(prev => [...prev, {
      role: "user",
      content: message,
      timestamp: new Date().toLocaleTimeString()
    }])

    // Send to ClawdBot
    const chatMsg = {
      type: "req",
      id: Math.random().toString(36).substring(2) + Date.now().toString(36),
      method: "chat.send",
      params: {
        message: message,
        sessionKey: "web-session-" + Math.random().toString(36).substring(2, 10),
        idempotencyKey: Math.random().toString(36).substring(2) + Date.now().toString(36)
      }
    }
    console.log("Sending message:", chatMsg)
    wsRef.current.send(JSON.stringify(chatMsg))
  }, [input, isConnected])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return (
    <div className="flex h-screen flex-col bg-[#050505] text-gray-200">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-800 bg-gray-900/50 px-6 py-4 backdrop-blur">
        <div className="flex items-center gap-3">
          <Bot className="h-6 w-6 text-cyan-400" />
          <h1 className="text-xl font-semibold text-white">ClawdBot Integration</h1>
          <span className="ml-2 rounded-full bg-gray-800 px-2 py-0.5 text-xs text-gray-400">
            ws://localhost:17500
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className={cn(
              "h-2 w-2 rounded-full",
              isConnected ? "bg-green-500 shadow-[0_0_10px_#22c55e]" : 
              isConnecting ? "bg-yellow-500 animate-pulse" : "bg-red-500"
            )} />
            <span className="text-sm text-gray-400">{connectionStatus}</span>
          </div>
          <button
            onClick={isConnected ? disconnect : connect}
            disabled={isConnecting}
            className={cn(
              "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50",
              isConnected 
                ? "bg-red-500/20 text-red-400 hover:bg-red-500/30" 
                : "bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30"
            )}
          >
            <Power className="h-4 w-4" />
            {isConnecting ? "Connecting..." : isConnected ? "Disconnect" : "Connect"}
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-gray-500">
            <Bot className="mb-4 h-16 w-16 opacity-20" />
            <p className="text-lg">Connect to ClawdBot to start chatting</p>
            <p className="text-sm">Click the Connect button above</p>
          </div>
        )}
        
        <div className="mx-auto max-w-4xl space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "flex gap-4 rounded-lg p-4",
                msg.role === "user" ? "bg-gray-800/50 ml-12" :
                msg.role === "assistant" ? "bg-cyan-900/20 mr-12 border border-cyan-800/30" :
                "bg-gray-900/30 mx-12 text-center text-sm text-gray-500"
              )}
            >
              {msg.role !== "system" && (
                <div className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                  msg.role === "user" ? "bg-gray-700" : "bg-cyan-500/20"
                )}>
                  {msg.role === "user" ? 
                    <User className="h-4 w-4" /> : 
                    <Bot className="h-4 w-4 text-cyan-400" />
                  }
                </div>
              )}
              <div className="flex-1">
                <div className="mb-1 flex items-center gap-2">
                  <span className={cn(
                    "text-sm font-medium",
                    msg.role === "user" ? "text-gray-300" :
                    msg.role === "assistant" ? "text-cyan-400" : "text-gray-500"
                  )}>
                    {msg.role === "user" ? "You" : 
                     msg.role === "assistant" ? "ClawdBot" : "System"}
                  </span>
                  {msg.timestamp && (
                    <span className="text-xs text-gray-600">{msg.timestamp}</span>
                  )}
                </div>
                <p className="text-gray-300 whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 bg-gray-900/50 p-4">
        <div className="mx-auto flex max-w-4xl gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isConnected ? "Type a message..." : "Connect first to send messages"}
            disabled={!isConnected}
            className="flex-1 rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white placeholder-gray-500 outline-none focus:border-cyan-500 disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={!isConnected || !input.trim()}
            className="flex items-center gap-2 rounded-lg bg-cyan-500 px-6 py-3 font-medium text-black transition-colors hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
