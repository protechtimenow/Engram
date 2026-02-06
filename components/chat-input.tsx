"use client"

import { useRef, type KeyboardEvent, type ChangeEvent } from "react"
import { Send } from "lucide-react"

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  disabled: boolean
}

export function ChatInput({ value, onChange, onSend, disabled }: ChatInputProps) {
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
    <div className="bg-gradient-to-t from-background to-transparent px-10 pb-10 pt-5">
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
