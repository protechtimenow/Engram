"use client"

import { useState, useCallback } from "react"
import { Send, Bot, RotateCcw } from "lucide-react"

interface Message {
  role: "user" | "assistant"
  content: string
  model: string
  timestamp: string
}

const MODELS = {
  fast: [
    { id: "z-ai/glm-4.7-flash", name: "GLM 4.7 Flash", emoji: "⚡" },
    { id: "openai/gpt-4o-mini", name: "GPT-4o Mini", emoji: "🚀" },
  ],
  powerful: [
    { id: "anthropic/claude-opus-4.6", name: "Claude Opus 4.6", emoji: "🧠" },
    { id: "openai/gpt-4o", name: "GPT-4o", emoji: "💪" },
  ],
  reasoning: [
    { id: "openai/o1-mini", name: "o1 Mini", emoji: "🤔" },
    { id: "anthropic/claude-3-5-sonnet", name: "Claude 3.5 Sonnet", emoji: " " },
  ]
}

export default function ComparePage() {
  const [leftModel, setLeftModel] = useState("z-ai/glm-4.7-flash")
  const [rightModel, setRightModel] = useState("anthropic/claude-opus-4.6")
  const [input, setInput] = useState("")
  const [leftMessages, setLeftMessages] = useState<Message[]>([])
  const [rightMessages, setRightMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const sendToModel = async (model: string, message: string): Promise<string> => {
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Engram Hub"
      },
      body: JSON.stringify({
        model: model,
        messages: [{ role: "user", content: message }],
        max_tokens: 1000,
        ...(model.includes("claude") && { reasoning: { enabled: true } })
      }),
    })
    
    const data = await response.json()
    if (!response.ok) throw new Error(data.error?.message || "API error")
    return data.choices[0].message.content
  }

  const handleSend = useCallback(async () => {
    if (!input.trim() || isLoading) return
    
    const message = input.trim()
    setInput("")
    setIsLoading(true)

    // Add user message to both sides
    const userMsg: Message = {
      role: "user",
      content: message,
      model: "user",
      timestamp: new Date().toLocaleTimeString()
    }
    setLeftMessages(prev => [...prev, userMsg])
    setRightMessages(prev => [...prev, userMsg])

    // Send to both models concurrently
    try {
      const [leftResponse, rightResponse] = await Promise.all([
        sendToModel(leftModel, message),
        sendToModel(rightModel, message)
      ])

      setLeftMessages(prev => [...prev, {
        role: "assistant",
        content: leftResponse,
        model: leftModel,
        timestamp: new Date().toLocaleTimeString()
      }])

      setRightMessages(prev => [...prev, {
        role: "assistant",
        content: rightResponse,
        model: rightModel,
        timestamp: new Date().toLocaleTimeString()
      }])
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Error"
      setLeftMessages(prev => [...prev, {
        role: "assistant",
        content: `Error: ${errorMsg}`,
        model: leftModel,
        timestamp: new Date().toLocaleTimeString()
      }])
      setRightMessages(prev => [...prev, {
        role: "assistant",
        content: `Error: ${errorMsg}`,
        model: rightModel,
        timestamp: new Date().toLocaleTimeString()
      }])
    } finally {
      setIsLoading(false)
    }
  }, [input, isLoading, leftModel, rightModel])

  const clearChat = () => {
    setLeftMessages([])
    setRightMessages([])
  }

  const getModelName = (id: string) => {
    for (const category of Object.values(MODELS)) {
      const model = category.find(m => m.id === id)
      if (model) return `${model.emoji} ${model.name}`
    }
    return id
  }

  return (
    <div className="flex h-screen flex-col bg-[#050505] text-gray-200">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-800 bg-gray-900/50 px-6 py-4">
        <div className="flex items-center gap-3">
          <Bot className="h-6 w-6 text-purple-400" />
          <h1 className="text-xl font-semibold text-white">Model Comparison</h1>
          <span className="ml-2 rounded-full bg-gray-800 px-2 py-0.5 text-xs text-gray-400">
            A2A Preview
          </span>
        </div>
        <button
          onClick={clearChat}
          className="flex items-center gap-2 rounded-lg bg-gray-800 px-4 py-2 text-sm text-gray-400 transition-colors hover:bg-gray-700"
        >
          <RotateCcw className="h-4 w-4" />
          Clear
        </button>
      </header>

      {/* Model Selectors */}
      <div className="flex border-b border-gray-800 bg-gray-900/30">
        <div className="flex-1 border-r border-gray-800 p-4">
          <label className="mb-2 block text-xs font-semibold uppercase tracking-widest text-gray-500">
            Model A (Left)
          </label>
          <select
            value={leftModel}
            onChange={(e) => setLeftModel(e.target.value)}
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm outline-none focus:border-purple-500"
          >
            <optgroup label="Fast & Cheap">
              {MODELS.fast.map(m => <option key={m.id} value={m.id}>{m.emoji} {m.name}</option>)}
            </optgroup>
            <optgroup label="Powerful">
              {MODELS.powerful.map(m => <option key={m.id} value={m.id}>{m.emoji} {m.name}</option>)}
            </optgroup>
            <optgroup label="Reasoning">
              {MODELS.reasoning.map(m => <option key={m.id} value={m.id}>{m.emoji} {m.name}</option>)}
            </optgroup>
          </select>
        </div>
        <div className="flex-1 p-4">
          <label className="mb-2 block text-xs font-semibold uppercase tracking-widest text-gray-500">
            Model B (Right)
          </label>
          <select
            value={rightModel}
            onChange={(e) => setRightModel(e.target.value)}
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm outline-none focus:border-purple-500"
          >
            <optgroup label="Fast & Cheap">
              {MODELS.fast.map(m => <option key={m.id} value={m.id}>{m.emoji} {m.name}</option>)}
            </optgroup>
            <optgroup label="Powerful">
              {MODELS.powerful.map(m => <option key={m.id} value={m.id}>{m.emoji} {m.name}</option>)}
            </optgroup>
            <optgroup label="Reasoning">
              {MODELS.reasoning.map(m => <option key={m.id} value={m.id}>{m.emoji} {m.name}</option>)}
            </optgroup>
          </select>
        </div>
      </div>

      {/* Chat Areas */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel */}
        <div className="flex-1 overflow-y-auto border-r border-gray-800 p-4">
          <h3 className="mb-4 text-center text-sm font-medium text-purple-400">
            {getModelName(leftModel)}
          </h3>
          <div className="space-y-4">
            {leftMessages.map((msg, i) => (
              <div
                key={i}
                className={`rounded-lg p-3 ${
                  msg.role === "user" 
                    ? "bg-purple-900/20 ml-8 border border-purple-800/30" 
                    : "bg-gray-800/50 mr-8"
                }`}
              >
                <div className="mb-1 text-xs text-gray-500">
                  {msg.role === "user" ? "You" : getModelName(msg.model)}
                </div>
                <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="mb-4 text-center text-sm font-medium text-cyan-400">
            {getModelName(rightModel)}
          </h3>
          <div className="space-y-4">
            {rightMessages.map((msg, i) => (
              <div
                key={i}
                className={`rounded-lg p-3 ${
                  msg.role === "user" 
                    ? "bg-cyan-900/20 ml-8 border border-cyan-800/30" 
                    : "bg-gray-800/50 mr-8"
                }`}
              >
                <div className="mb-1 text-xs text-gray-500">
                  {msg.role === "user" ? "You" : getModelName(msg.model)}
                </div>
                <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 bg-gray-900/50 p-4">
        <div className="mx-auto flex max-w-4xl gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type a message to compare both models..."
            disabled={isLoading}
            className="flex-1 rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white placeholder-gray-500 outline-none focus:border-purple-500 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-purple-500 to-cyan-500 px-6 py-3 font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
            {isLoading ? "Comparing..." : "Compare"}
          </button>
        </div>
      </div>
    </div>
  )
}
