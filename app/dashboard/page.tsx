"use client"

import { useState, useEffect } from "react"
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity,
  Target,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  Scale,
  ArrowRight,
  Plus,
  RefreshCw
} from "lucide-react"
import Link from "next/link"

interface Position {
  id: string
  asset: string
  type: "LONG" | "SHORT"
  entryPrice: number
  currentPrice: number
  size: number
  stopLoss: number
  takeProfit: number
  pnl: number
  pnlPercent: number
  status: "OPEN" | "CLOSED"
  openedAt: string
  debateId?: string
}

interface DebateTrade {
  id: string
  asset: string
  signal: "LONG" | "SHORT" | "NEUTRAL"
  entry: number
  target: number
  stop: number
  position: number
  confidence: number
  timestamp: string
  executed: boolean
}

interface PortfolioStats {
  totalPnl: number
  openPositions: number
  winRate: number
  avgTrade: number
  maxDrawdown: number
  portfolioHeat: number
}

export default function DashboardPage() {
  const [positions, setPositions] = useState<Position[]>([])
  const [recentDebates, setRecentDebates] = useState<DebateTrade[]>([])
  const [stats, setStats] = useState<PortfolioStats>({
    totalPnl: 0,
    openPositions: 0,
    winRate: 0,
    avgTrade: 0,
    maxDrawdown: 0,
    portfolioHeat: 0
  })
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isUpdating, setIsUpdating] = useState(false)

  // Load data from localStorage
  useEffect(() => {
    const loadData = () => {
      const savedPositions = localStorage.getItem('trading_positions')
      const savedDebates = localStorage.getItem('a2a_debate_session')
      
      if (savedPositions) {
        try {
          setPositions(JSON.parse(savedPositions))
        } catch (e) {
          console.error('Failed to load positions:', e)
        }
      } else {
        // Demo data for first-time users
        setPositions([
          {
            id: "1",
            asset: "BTC/USDT",
            type: "LONG",
            entryPrice: 64800,
            currentPrice: 65600,
            size: 0.15,
            stopLoss: 63000,
            takeProfit: 68000,
            pnl: 120,
            pnlPercent: 1.23,
            status: "OPEN",
            openedAt: new Date(Date.now() - 86400000).toISOString()
          },
          {
            id: "2",
            asset: "ETH/USDT",
            type: "SHORT",
            entryPrice: 3520,
            currentPrice: 3480,
            size: 2.5,
            stopLoss: 3600,
            takeProfit: 3200,
            pnl: 100,
            pnlPercent: 1.14,
            status: "OPEN",
            openedAt: new Date(Date.now() - 172800000).toISOString()
          }
        ])
      }

      if (savedDebates) {
        try {
          const debate = JSON.parse(savedDebates)
          if (debate.topic && debate.id) {
            // Extract trade info from debate
            setRecentDebates([{
              id: debate.id,
              asset: debate.extractedPair || "BTC/USDT",
              signal: "LONG",
              entry: 64800,
              target: 68000,
              stop: 63000,
              position: 10,
              confidence: 75,
              timestamp: debate.createdAt,
              executed: false
            }])
          }
        } catch (e) {
          console.error('Failed to load debates:', e)
        }
      }

      setIsLoading(false)
    }

    loadData()
  }, [])

  // Calculate stats
  useEffect(() => {
    const openPos = positions.filter(p => p.status === "OPEN")
    const totalPnl = positions.reduce((sum, p) => sum + p.pnl, 0)
    const winningTrades = positions.filter(p => p.pnl > 0).length
    const winRate = positions.length > 0 ? (winningTrades / positions.length) * 100 : 0
    const avgTrade = positions.length > 0 ? totalPnl / positions.length : 0
    const portfolioHeat = openPos.reduce((sum, p) => sum + Math.abs(p.pnlPercent), 0)

    setStats({
      totalPnl,
      openPositions: openPos.length,
      winRate,
      avgTrade,
      maxDrawdown: -5.2,
      portfolioHeat
    })
  }, [positions])

  // Fetch live prices for open positions
  const fetchLivePrices = async () => {
    const openPositions = positions.filter(p => p.status === "OPEN")
    if (openPositions.length === 0) return

    setIsUpdating(true)
    try {
      // Get unique symbols
      const symbols = [...new Set(openPositions.map(p => p.asset.replace('/', '')))]
      
      const response = await fetch(`/api/prices?symbols=${symbols.join(',')}`)
      const data = await response.json()

      if (data.success) {
        // Update positions with new prices
        setPositions(prev => {
          const updated = prev.map(position => {
            if (position.status !== "OPEN") return position
            
            const symbol = position.asset.replace('/', '')
            const priceData = data.data[symbol]
            
            if (priceData?.price) {
              const currentPrice = priceData.price
              const priceDiff = currentPrice - position.entryPrice
              const pnl = position.type === "LONG" 
                ? priceDiff * position.size 
                : -priceDiff * position.size
              const pnlPercent = (pnl / (position.entryPrice * position.size)) * 100
              
              return {
                ...position,
                currentPrice,
                pnl,
                pnlPercent
              }
            }
            return position
          })
          
          // Save to localStorage
          localStorage.setItem('trading_positions', JSON.stringify(updated))
          return updated
        })
        
        setLastUpdated(new Date())
      }
    } catch (error) {
      console.error('Failed to fetch live prices:', error)
    } finally {
      setIsUpdating(false)
    }
  }

  // Poll for price updates every 10 seconds
  useEffect(() => {
    if (positions.filter(p => p.status === "OPEN").length === 0) return

    // Initial fetch
    fetchLivePrices()

    // Set up polling
    const interval = setInterval(fetchLivePrices, 10000) // 10 seconds

    return () => clearInterval(interval)
  }, [positions.length]) // Re-run when positions change

  const closePosition = (id: string) => {
    setPositions(prev => prev.map(p => 
      p.id === id ? { ...p, status: "CLOSED" } : p
    ))
    // Save to localStorage
    const updated = positions.map(p => p.id === id ? { ...p, status: "CLOSED" } : p)
    localStorage.setItem('trading_positions', JSON.stringify(updated))
  }

  const executeTrade = (debate: DebateTrade) => {
    // Skip NEUTRAL signals - can't execute a neutral position
    if (debate.signal === "NEUTRAL") {
      alert("Cannot execute NEUTRAL signal. Only LONG or SHORT positions can be created.")
      return
    }
    
    const newPosition: Position = {
      id: Date.now().toString(),
      asset: debate.asset,
      type: debate.signal, // Now guaranteed to be "LONG" | "SHORT"
      entryPrice: debate.entry,
      currentPrice: debate.entry, // Would fetch real price
      size: debate.position / 100, // Convert % to size
      stopLoss: debate.stop,
      takeProfit: debate.target,
      pnl: 0,
      pnlPercent: 0,
      status: "OPEN",
      openedAt: new Date().toISOString(),
      debateId: debate.id
    }

    const updated = [...positions, newPosition]
    setPositions(updated)
    localStorage.setItem('trading_positions', JSON.stringify(updated))

    // Mark debate as executed
    setRecentDebates(prev => prev.map(d => 
      d.id === debate.id ? { ...d, executed: true } : d
    ))
  }

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#050505]">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-purple-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#050505] text-gray-200">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-green-500 to-emerald-500">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-white">Trading Dashboard</h1>
              <p className="text-xs text-gray-500">Live positions & debate-driven trades</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link 
              href="/a2a"
              className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700"
            >
              <Plus className="h-4 w-4" />
              New Debate
            </Link>
          </div>
        </div>
      </header>

      <main className="p-6">
        {/* Stats Row */}
        <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard 
            title="Total P&L"
            value={`$${stats.totalPnl.toFixed(2)}`}
            change={`${stats.totalPnl >= 0 ? '+' : ''}${stats.totalPnl.toFixed(2)}`}
            positive={stats.totalPnl >= 0}
            icon={stats.totalPnl >= 0 ? TrendingUp : TrendingDown}
          />
          <StatCard 
            title="Open Positions"
            value={stats.openPositions.toString()}
            change={`${stats.portfolioHeat.toFixed(1)}% heat`}
            icon={Activity}
          />
          <StatCard 
            title="Win Rate"
            value={`${stats.winRate.toFixed(1)}%`}
            change={`${positions.filter(p => p.pnl > 0).length}/${positions.length} trades`}
            positive={stats.winRate > 50}
            icon={Target}
          />
          <StatCard 
            title="Avg Trade"
            value={`$${stats.avgTrade.toFixed(2)}`}
            change={`${stats.avgTrade >= 0 ? '+' : ''}${stats.avgTrade.toFixed(2)}`}
            positive={stats.avgTrade >= 0}
            icon={DollarSign}
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Active Positions */}
          <div className="lg:col-span-2">
            <div className="rounded-xl border border-gray-800 bg-gray-900/30">
              <div className="flex items-center justify-between border-b border-gray-800 px-4 py-3">
                <h2 className="flex items-center gap-2 font-semibold text-white">
                  <Activity className="h-4 w-4 text-green-400" />
                  Active Positions
                </h2>
                <div className="flex items-center gap-3">
                  {lastUpdated && (
                    <span className="text-xs text-gray-500">
                      Updated: {lastUpdated.toLocaleTimeString()}
                      {isUpdating && <span className="ml-1 text-green-400">...</span>}
                    </span>
                  )}
                  <button 
                    onClick={fetchLivePrices}
                    disabled={isUpdating}
                    className="rounded p-1 text-gray-500 hover:bg-gray-800 hover:text-gray-300 disabled:opacity-50"
                  >
                    <RefreshCw className={`h-4 w-4 ${isUpdating ? 'animate-spin' : ''}`} />
                  </button>
                </div>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-800/50 text-left text-xs text-gray-500">
                    <tr>
                      <th className="px-4 py-2">Asset</th>
                      <th className="px-4 py-2">Type</th>
                      <th className="px-4 py-2">Entry</th>
                      <th className="px-4 py-2">Current</th>
                      <th className="px-4 py-2">Size</th>
                      <th className="px-4 py-2">P&L</th>
                      <th className="px-4 py-2">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {positions.filter(p => p.status === "OPEN").map((position) => (
                      <tr key={position.id} className="border-t border-gray-800 hover:bg-gray-800/30">
                        <td className="px-4 py-3 font-medium text-white">{position.asset}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs ${
                            position.type === "LONG" 
                              ? "bg-green-500/20 text-green-400" 
                              : "bg-red-500/20 text-red-400"
                          }`}>
                            {position.type === "LONG" ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                            {position.type}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-400">${position.entryPrice.toLocaleString()}</td>
                        <td className="px-4 py-3 text-gray-400">${position.currentPrice.toLocaleString()}</td>
                        <td className="px-4 py-3 text-gray-400">{position.size}</td>
                        <td className="px-4 py-3">
                          <span className={position.pnl >= 0 ? "text-green-400" : "text-red-400"}>
                            {position.pnl >= 0 ? '+' : ''}${position.pnl.toFixed(2)}
                            <span className="text-xs text-gray-500"> ({position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%)</span>
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => closePosition(position.id)}
                            className="rounded bg-gray-700 px-2 py-1 text-xs text-gray-300 hover:bg-gray-600"
                          >
                            Close
                          </button>
                        </td>
                      </tr>
                    ))}
                    {positions.filter(p => p.status === "OPEN").length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                          No open positions. Start a debate to generate trade signals.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Trade History */}
            <div className="mt-6 rounded-xl border border-gray-800 bg-gray-900/30">
              <div className="border-b border-gray-800 px-4 py-3">
                <h2 className="flex items-center gap-2 font-semibold text-white">
                  <Clock className="h-4 w-4 text-gray-400" />
                  Recent Trade History
                </h2>
              </div>
              <div className="p-4">
                {positions.filter(p => p.status === "CLOSED").slice(0, 5).map((position) => (
                  <div key={position.id} className="mb-2 flex items-center justify-between rounded-lg bg-gray-800/50 px-4 py-2 text-sm">
                    <div className="flex items-center gap-3">
                      <span className={position.pnl >= 0 ? "text-green-400" : "text-red-400"}>
                        {position.pnl >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                      </span>
                      <span className="font-medium text-white">{position.asset}</span>
                      <span className="text-gray-500">{position.type}</span>
                    </div>
                    <span className={position.pnl >= 0 ? "text-green-400" : "text-red-400"}>
                      {position.pnl >= 0 ? '+' : ''}${position.pnl.toFixed(2)}
                    </span>
                  </div>
                ))}
                {positions.filter(p => p.status === "CLOSED").length === 0 && (
                  <p className="py-4 text-center text-sm text-gray-500">No closed trades yet</p>
                )}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Recent Debates */}
            <div className="rounded-xl border border-gray-800 bg-gray-900/30">
              <div className="border-b border-gray-800 px-4 py-3">
                <h2 className="flex items-center gap-2 font-semibold text-white">
                  <Scale className="h-4 w-4 text-purple-400" />
                  Recent Debates
                </h2>
              </div>
              <div className="p-4">
                {recentDebates.map((debate) => (
                  <div key={debate.id} className="mb-3 rounded-lg border border-gray-700 bg-gray-800/30 p-3">
                    <div className="mb-2 flex items-center justify-between">
                      <span className="font-medium text-white">{debate.asset}</span>
                      <span className={`rounded px-2 py-0.5 text-xs ${
                        debate.signal === "LONG" ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
                      }`}>
                        {debate.signal}
                      </span>
                    </div>
                    <div className="mb-2 grid grid-cols-2 gap-2 text-xs text-gray-400">
                      <div>Entry: ${debate.entry.toLocaleString()}</div>
                      <div>Target: ${debate.target.toLocaleString()}</div>
                      <div>Stop: ${debate.stop.toLocaleString()}</div>
                      <div>Size: {debate.position}%</div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        Confidence: {debate.confidence}%
                      </span>
                      {!debate.executed ? (
                        <button
                          onClick={() => executeTrade(debate)}
                          className="flex items-center gap-1 rounded bg-green-600 px-3 py-1 text-xs font-medium text-white hover:bg-green-700"
                        >
                          Execute
                          <ArrowRight className="h-3 w-3" />
                        </button>
                      ) : (
                        <span className="flex items-center gap-1 text-xs text-green-400">
                          <CheckCircle className="h-3 w-3" />
                          Executed
                        </span>
                      )}
                    </div>
                  </div>
                ))}
                {recentDebates.length === 0 && (
                  <div className="py-4 text-center">
                    <p className="mb-2 text-sm text-gray-500">No recent debates</p>
                    <Link 
                      href="/a2a"
                      className="inline-flex items-center gap-1 text-sm text-purple-400 hover:text-purple-300"
                    >
                      Start a debate
                      <ArrowRight className="h-3 w-3" />
                    </Link>
                  </div>
                )}
              </div>
            </div>

            {/* Risk Metrics */}
            <div className="rounded-xl border border-gray-800 bg-gray-900/30">
              <div className="border-b border-gray-800 px-4 py-3">
                <h2 className="flex items-center gap-2 font-semibold text-white">
                  <AlertTriangle className="h-4 w-4 text-amber-400" />
                  Risk Metrics
                </h2>
              </div>
              <div className="p-4 space-y-3">
                <RiskBar 
                  label="Portfolio Heat" 
                  value={stats.portfolioHeat} 
                  max={20} 
                  color={stats.portfolioHeat > 15 ? "red" : stats.portfolioHeat > 10 ? "amber" : "green"}
                />
                <RiskBar 
                  label="Max Drawdown" 
                  value={Math.abs(stats.maxDrawdown)} 
                  max={20} 
                  color={Math.abs(stats.maxDrawdown) > 15 ? "red" : Math.abs(stats.maxDrawdown) > 10 ? "amber" : "green"}
                />
                <div className="mt-4 rounded bg-gray-800/50 p-3 text-xs">
                  <div className="mb-1 flex justify-between text-gray-400">
                    <span>Position Risk</span>
                    <span className={stats.portfolioHeat > 15 ? "text-red-400" : "text-green-400"}>
                      {stats.portfolioHeat > 15 ? "HIGH" : stats.portfolioHeat > 10 ? "MEDIUM" : "LOW"}
                    </span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>Win Rate</span>
                    <span className={stats.winRate > 50 ? "text-green-400" : "text-amber-400"}>
                      {stats.winRate.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

// Components
function StatCard({ 
  title, 
  value, 
  change, 
  positive = true, 
  icon: Icon 
}: { 
  title: string
  value: string
  change: string
  positive?: boolean
  icon: any
}) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900/30 p-4">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs text-gray-500">{title}</span>
        <Icon className="h-4 w-4 text-gray-600" />
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className={`text-xs ${positive ? 'text-green-400' : 'text-red-400'}`}>
        {change}
      </div>
    </div>
  )
}

function RiskBar({ 
  label, 
  value, 
  max, 
  color 
}: { 
  label: string
  value: number
  max: number
  color: "red" | "amber" | "green"
}) {
  const percentage = Math.min((value / max) * 100, 100)
  const colorClasses = {
    red: "bg-red-500",
    amber: "bg-amber-500",
    green: "bg-green-500"
  }

  return (
    <div>
      <div className="mb-1 flex justify-between text-xs">
        <span className="text-gray-400">{label}</span>
        <span className="text-gray-500">{value.toFixed(1)}%</span>
      </div>
      <div className="h-2 rounded-full bg-gray-800">
        <div 
          className={`h-full rounded-full ${colorClasses[color]} transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
