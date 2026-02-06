"use client"

import { useState } from "react"

interface SidebarProps {
  selectedModel: string
  onModelChange: (model: string) => void
  onToggleTerminal: () => void
  terminalVisible: boolean
}

export function Sidebar({
  selectedModel,
  onModelChange,
  onToggleTerminal,
  terminalVisible,
}: SidebarProps) {
  const [fingerprints] = useState<
    { tokenId: string; label: string }[]
  >([])

  return (
    <aside className="flex w-80 shrink-0 flex-col border-r border-border bg-card/70 p-5 backdrop-blur-xl">
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
        <div className="space-y-2">
          <div className="flex items-center gap-2 rounded-xl border border-border bg-muted/30 px-3 py-2.5 text-sm">
            <span className="inline-block h-2 w-2 rounded-full bg-primary shadow-[0_0_10px_hsl(var(--primary))]" />
            Local Engram Model
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-border bg-muted/30 px-3 py-2.5 text-sm">
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
          <option value="custom">Custom Engine...</option>
        </select>
      </div>

      <div className="mb-6">
        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Neural Fingerprints (Live Context)
        </p>
        <div className="max-h-48 space-y-2 overflow-y-auto">
          {fingerprints.length === 0 ? (
            <div className="rounded-xl border border-border bg-muted/30 px-3 py-2.5 text-sm opacity-50">
              Scanning codebase...
            </div>
          ) : (
            fingerprints.map((fp) => (
              <div
                key={fp.tokenId}
                className="rounded-xl border border-border bg-muted/30 px-3 py-2.5 font-mono text-xs"
              >
                <span className="text-primary">#{fp.tokenId}</span>{" "}
                {fp.label}
              </div>
            ))
          )}
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
