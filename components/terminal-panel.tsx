"use client"

import { cn } from "../lib/utils"

export interface TerminalLine {
  text: string
  type: "cmd" | "out"
}

export function TerminalPanel({
  visible,
  lines,
}: {
  visible: boolean
  lines: TerminalLine[]
}) {
  if (!visible) return null

  return (
    <div className="h-48 overflow-y-auto border-t border-border bg-[hsl(0,0%,2%)] p-4 font-mono text-sm">
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
