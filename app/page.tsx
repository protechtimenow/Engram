"use client"

import { useState, useCallback } from "react"
import { Sidebar } from "../components/sidebar"
import { ChatMessages, type Message } from "../components/chat-messages"
import { ChatInput } from "../components/chat-input"
import { TerminalPanel, type TerminalLine } from "../components/terminal-panel"

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

    // Handle slash commands
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
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: resultMsg },
        ])
      } catch (err) {
        const errorMsg =
          err instanceof Error ? err.message : "Unknown error"
        addTerminalLine(`Error: ${errorMsg}`, "out")
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Failed to execute OpenCode command: ${errorMsg}`,
          },
        ])
      } finally {
        setIsLoading(false)
      }
      return
    }

    // Chat completion
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
        const content = data.choices[0].message.content
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content },
        ])
      } else {
        const errorMsg =
          data.detail || data.error?.message || "Unknown AI server error"
        throw new Error(errorMsg)
      }
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Unknown error"
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
