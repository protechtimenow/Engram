"use client"

import { useState, useRef, useEffect } from "react"
import {
  Users,
  Send,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  MessageSquare,
  RotateCcw,
  Brain,
  Scale,
  Target,
  Terminal,
  ChevronDown,
  ChevronUp,
  Code2,
  BarChart3,
  Shield,
  Calculator,
  Lightbulb,
  DollarSign,
  Zap
} from "lucide-react"

interface ScriptData {
  marketAnalysis?: any
  confidenceScore?: any
  kellyCalculation?: any
}

interface DebateMessage {
  role: "user" | "assistant"
  content: string
  agent?: "proposer" | "critic" | "consensus"
  timestamp: string
  scriptData?: any
}

interface DebateSession {
  id: string
  topic: string
  messages: DebateMessage[]
  status: "active" | "completed"
  extractedPair?: string
  tierDistribution?: {
    proposer: string
    critic: string
    consensus: string
  }
  estimatedCost?: number
  routingEnabled?: boolean
}

interface TierConfig {
  SIMPLE: {
    model: string
    description: string
    price: string
  }
  MEDIUM: {
    model: string
    description: string
    price: string
  }
  COMPLEX: {
    model: string
    description: string
    price: string
  }
  REASONING: {
    model: string
    description: string
    price: string
  }
}

const AGENT_CONFIG = {
  proposer: {
    name: "Proposer",
    icon: Target,
    color: "purple",
    bgColor: "bg-purple-500/10",
    borderColor: "border-purple-500/30",
    textColor: "text-purple-400",
    description: "Builds the initial trading strategy",
    scriptIcon: Target,
    scriptName: "analyze_market.py",
    tierConfig: {
      SIMPLE: { model: "DeepSeek Chat", price: "$0.28/M" },
      MEDIUM: { model: "GPT-4o Mini", price: "$0.15/M" },
      COMPLEX: { model: "Claude Opus 4.6", price: "$75/M" },
      REASONING: { model: "DeepSeek R1", price: "$2.78/M" }
    }
  },
  critic: {
    name: "Critic",
    icon: AlertTriangle,
    color: "amber",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/30",
    textColor: "text-amber-400",
    description: "Challenges assumptions & finds risks",
    scriptIcon: AlertTriangle,
    scriptName: "confidence_scoring.py",
    tierConfig: {
      SIMPLE: { model: "DeepSeek Chat", price: "$0.28/M" },
      MEDIUM: { model: "GPT-4o Mini", price: "$0.15/M" },
      COMPLEX: { model: "Claude Sonnet", price: "$3.00/M" },
      REASONING: { model: "DeepSeek R1", price: "$2.78/M" }
    }
  },
  consensus: {
    name: "Consensus",
    icon: Scale,
    color: "cyan",
    bgColor: "bg-cyan-500/10",
    borderColor: "border-cyan-500/30",
    textColor: "text-cyan-400",
    description: "Synthesizes final recommendation",
    scriptIcon: Calculator,
    scriptName: "decision_nets.py",
    tierConfig: {
      SIMPLE: { model: "DeepSeek Chat", price: "$0.28/M" },
      MEDIUM: { model: "GPT-4o Mini", price: "$0.15/M" },
      COMPLEX: { model: "Claude Sonnet", price: "$3.00/M" },
      REASONING: { model: "DeepSeek R1", price: "$2.78/M" }
    }
  }
}

// Script Results Panel Component
function ScriptResultsPanel({ data, agent, tierDistribution }: { data: any; agent: string; tierDistribution?: { proposer: string; critic: string; consensus: string } }) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  if (!data) return null
  
  const config = AGENT_CONFIG[agent as keyof typeof AGENT_CONFIG]
  const ScriptIcon = config?.scriptIcon || Code2
  const tier = (tierDistribution?.[agent as keyof typeof tierDistribution] || 'SIMPLE')
  const tierConfig = config?.tierConfig?.[tier as keyof typeof config.tierConfig] || config?.tierConfig?.SIMPLE

  return (
    <div className="mt-3 rounded-lg border border-gray-700/50 bg-gray-900/50">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between px-3 py-2 text-left text-xs text-gray-400 hover:text-gray-300"
      >
        <div className="flex items-center gap-2">
          <Zap className="h-3 w-3 text-yellow-400" />
          <span>Tier: <span className="text-yellow-400 font-semibold">{tier}</span></span>
          {data.error ? (
            <span className="text-red-400">(error)</span>
          ) : (
            <span className="text-green-400">(success)</span>
          )}
          <span className="ml-2 rounded-full bg-blue-500/10 px-2 py-0.5 text-xs text-blue-400">{tierConfig?.price}</span>
        </div>
        {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
      </button>

      {isExpanded && (
        <div className="border-t border-gray-700/50 px-3 py-2">
          <div className="mb-2 text-xs text-gray-400">
            <span className="font-semibold">Model: </span>{tierConfig?.model}
          </div>
          <pre className="max-h-48 overflow-auto text-xs text-gray-500">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default function A2APage() {
  const [topic, setTopic] = useState("")
  const [context, setContext] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [session, setSession] = useState<DebateSession | null>(null)
  const [followUp, setFollowUp] = useState("")
  const [scriptResults, setScriptResults] = useState<ScriptData | null>(null)
  const [extractedPair, setExtractedPair] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSession = localStorage.getItem('a2a_debate_session')
    const savedPair = localStorage.getItem('a2a_debate_pair')
    if (savedSession) {
      try {
        setSession(JSON.parse(savedSession))
        if (savedPair) setExtractedPair(savedPair)
      } catch (e) {
        console.error('Failed to load saved session:', e)
      }
    }
  }, [])

  // Save session to localStorage when it changes
  useEffect(() => {
    if (session) {
      localStorage.setItem('a2a_debate_session', JSON.stringify(session))
      if (extractedPair) localStorage.setItem('a2a_debate_pair', extractedPair)
    } else {
      localStorage.removeItem('a2a_debate_session')
      localStorage.removeItem('a2a_debate_pair')
    }
  }, [session, extractedPair])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [session?.messages])

  const startDebate = async () => {
    if (!topic.trim() || isLoading) return
    
    setIsLoading(true)
    setScriptResults(null)
    try {
      const response = await fetch("/api/a2a/debate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "start",
          topic: topic.trim(),
          context: context.trim() || undefined,
          useScripts: true
        })
      })

      const data = await response.json()
      if (data.success) {
        setSession(data.session)
        setExtractedPair(data.extractedPair || null)
        setScriptResults(data.results?.scriptResults || null)
      } else {
        throw new Error(data.error)
      }
    } catch (error) {
      console.error("Failed to start debate:", error)
      alert("Failed to start debate. Check console for details.")
    } finally {
      setIsLoading(false)
    }
  }

  const sendFollowUp = async () => {
    if (!followUp.trim() || !session || isLoading) return

    setIsLoading(true)
    try {
      const response = await fetch("/api/a2a/debate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "continue",
          debateId: session.id,
          message: followUp.trim(),
          useScripts: true
        })
      })

      const data = await response.json()
      if (data.success) {
        setSession(data.session)
      } else if (data.error === "Debate not found") {
        // Server lost the session (in-memory storage cleared)
        alert("Session expired. Starting a new debate...")
        resetDebate()
      } else {
        throw new Error(data.error)
      }
    } catch (error) {
      console.error("Failed to continue debate:", error)
      alert("Failed to send message. The session may have expired. Try starting a new debate.")
    } finally {
      setIsLoading(false)
      setFollowUp("")
    }
  }

  const resetDebate = () => {
    setSession(null)
    setTopic("")
    setContext("")
    setFollowUp("")
    setScriptResults(null)
    setExtractedPair(null)
    localStorage.removeItem('a2a_debate_session')
    localStorage.removeItem('a2a_debate_pair')
  }

  const renderAgentMessage = (msg: DebateMessage) => {
    if (!msg.agent) return null
    
    const config = AGENT_CONFIG[msg.agent]
    const Icon = config.icon

    return (
      <div className={`mb-6 rounded-xl border ${config.borderColor} ${config.bgColor} p-4`}>
        <div className="mb-3 flex items-center gap-3">
          <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-${config.color}-500/20`}>
            <Icon className={`h-5 w-5 ${config.textColor}`} />
          </div>
          <div>
            <div className={`font-semibold ${config.textColor}`}>
              {config.name}
            </div>
            <div className="text-xs text-gray-500">
              {config.tierConfig.SIMPLE.model}
            </div>
          </div>
          <div className="ml-auto text-xs text-gray-600">
            {new Date(msg.timestamp).toLocaleTimeString()}
          </div>
        </div>
        <div className="whitespace-pre-wrap text-sm leading-relaxed text-gray-300">
          {msg.content}
        </div>
        
        {/* Script Results */}
        {msg.scriptData && (
          <ScriptResultsPanel data={msg.scriptData} agent={msg.agent} tierDistribution={session?.tierDistribution} />
        )}
      </div>
    )
  }

  const renderUserMessage = (msg: DebateMessage) => (
    <div className="mb-6 ml-12 flex justify-end">
      <div className="max-w-[80%] rounded-xl bg-gray-800/50 px-4 py-3 border border-gray-700">
        <div className="mb-1 text-xs text-gray-500">You</div>
        <div className="text-sm text-gray-200">{msg.content}</div>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen flex-col bg-[#050505] text-gray-200">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-800 bg-gray-900/50 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-cyan-500">
            <Users className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-white">A2A Debate</h1>
            <p className="text-xs text-gray-500">Multi-Agent Trading Analysis with Neural Core</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 rounded-full bg-gray-800/50 px-4 py-2 text-xs">
            <Terminal className="h-3 w-3 text-green-400" />
            <span className="text-gray-400">Python Scripts</span>
          </div>
          <div className="flex items-center gap-2 rounded-full bg-gray-800/50 px-4 py-2 text-xs">
            <Brain className="h-3 w-3 text-purple-400" />
            <span className="text-gray-400">3 Agents</span>
          </div>
          {session && (
            <button
              onClick={resetDebate}
              className="flex items-center gap-2 rounded-lg bg-gray-800 px-4 py-2 text-sm text-gray-400 transition-colors hover:bg-gray-700"
            >
              <RotateCcw className="h-4 w-4" />
              New Debate
            </button>
          )}
        </div>
      </header>

      {/* Agent Overview */}
      {!session && (
        <div className="grid grid-cols-3 gap-4 border-b border-gray-800 bg-gray-900/20 px-6 py-4">
          {Object.entries(AGENT_CONFIG).map(([key, config]) => {
            const Icon = config.icon
            const ScriptIcon = config.scriptIcon
            return (
              <div key={key} className={`rounded-xl border ${config.borderColor} ${config.bgColor} p-4`}>
                <div className="mb-2 flex items-center gap-2">
                  <Icon className={`h-4 w-4 ${config.textColor}`} />
                  <span className={`font-medium ${config.textColor}`}>{config.name}</span>
                </div>
                <div className="text-xs text-gray-500">{config.tierConfig.SIMPLE.model}</div>
                <div className="mt-2 text-xs text-gray-400">{config.description}</div>
                <div className="mt-2 flex items-center gap-1 text-xs text-green-400">
                  <ScriptIcon className="h-3 w-3" />
                  <span>{config.scriptName}</span>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {!session ? (
          <div className="mx-auto max-w-2xl space-y-6">
            <div className="text-center">
              <h2 className="mb-2 text-2xl font-semibold text-white">
                Start a Trading Analysis Debate
              </h2>
              <p className="text-gray-500">
                Three AI agents will analyze your trading scenario with Neural Core script integration
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-400">
                  Trading Scenario <span className="text-red-400">*</span>
                </label>
                <textarea
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., 'BTC is showing bullish divergence on the 4H chart with increasing volume. Should I enter a long position at $43,200?'"
                  className="h-32 w-full rounded-xl border border-gray-700 bg-gray-800/50 p-4 text-sm text-white placeholder-gray-600 outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                />
                {extractedPair && (
                  <div className="mt-2 text-xs text-green-400">
                    Detected pair: {extractedPair}
                  </div>
                )}
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-gray-400">
                  Additional Context <span className="text-gray-600">(optional)</span>
                </label>
                <textarea
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  placeholder="e.g., 'Portfolio size: $10k, Risk tolerance: medium, Timeframe: 1-2 weeks, Current positions: 50% ETH long'"
                  className="h-24 w-full rounded-xl border border-gray-700 bg-gray-800/50 p-4 text-sm text-white placeholder-gray-600 outline-none focus:border-purple-500"
                />
              </div>

              <button
                onClick={startDebate}
                disabled={!topic.trim() || isLoading}
                className="flex w-full items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 px-6 py-4 font-semibold text-white transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Running scripts & analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    Start Multi-Agent Analysis
                  </>
                )}
              </button>
            </div>

            {/* Script Integration Info */}
            <div className="rounded-xl border border-gray-800 bg-gray-900/30 p-4">
              <div className="mb-3 flex items-center gap-2 text-sm text-gray-400">
                <Code2 className="h-4 w-4" />
                Neural Core Script Integration
              </div>
              <div className="space-y-2 text-xs text-gray-500">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-3 w-3 text-purple-400" />
                  <span><strong>Proposer:</strong> Runs analyze_market.py for technical data</span>
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="h-3 w-3 text-amber-400" />
                  <span><strong>Critic:</strong> Runs confidence_scoring.py for bias detection</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calculator className="h-3 w-3 text-cyan-400" />
                  <span><strong>Consensus:</strong> Runs decision_nets.py for Kelly criterion sizing</span>
                </div>
              </div>
            </div>

            {/* Example Prompts */}
            <div className="rounded-xl border border-gray-800 bg-gray-900/30 p-4">
              <div className="mb-3 flex items-center gap-2 text-sm text-gray-500">
                <TrendingUp className="h-4 w-4" />
                Example Scenarios
              </div>
              <div className="space-y-2">
                {[
                  "ETH broke above $2,500 resistance on high volume. RSI at 68. Long or wait for pullback?",
                  "Fed raising rates tomorrow. Should I close my tech stock positions before the announcement?",
                  "SOL forming a head and shoulders pattern on daily. Short at $98 or is it a fakeout?"
                ].map((example, i) => (
                  <button
                    key={i}
                    onClick={() => setTopic(example)}
                    className="block w-full rounded-lg bg-gray-800/50 px-3 py-2 text-left text-sm text-gray-400 transition-colors hover:bg-gray-800 hover:text-gray-300"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-4xl">
            <div className="mb-6 rounded-xl border border-gray-800 bg-gray-900/30 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <MessageSquare className="h-4 w-4" />
                    Topic:
                  </div>
                  <div className="mt-1 text-white">{session.topic}</div>
                </div>
                {extractedPair && (
                  <div className="rounded-lg bg-green-500/10 px-3 py-1 text-xs text-green-400">
                    {extractedPair}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              {session.messages.map((msg, i) => (
                <div key={i}>
                  {msg.role === "user" 
                    ? renderUserMessage(msg) 
                    : renderAgentMessage(msg)
                  }
                </div>
              ))}
            </div>

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      {session && (
        <div className="border-t border-gray-800 bg-gray-900/50 p-4">
          <div className="mx-auto flex max-w-4xl gap-4">
            <input
              type="text"
              value={followUp}
              onChange={(e) => setFollowUp(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendFollowUp()}
              placeholder="Ask a follow-up question to all three agents..."
              disabled={isLoading}
              className="flex-1 rounded-xl border border-gray-700 bg-gray-800 px-4 py-3 text-white placeholder-gray-500 outline-none focus:border-purple-500 disabled:opacity-50"
            />
            <button
              onClick={sendFollowUp}
              disabled={isLoading || !followUp.trim()}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-500 to-cyan-500 px-6 py-3 font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
              {isLoading ? "Thinking..." : "Send"}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
