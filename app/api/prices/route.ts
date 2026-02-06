import { NextRequest, NextResponse } from "next/server";

// Extended cache to reduce API calls (60 seconds)
const priceCache = new Map<string, { price: number; timestamp: number; source: string }>();
const CACHE_TTL = 60000; // 60 seconds
const REQUEST_TRACKER: { count: number; resetTime: number } = { count: 0, resetTime: 0 };
const MAX_REQUESTS_PER_MINUTE = 25; // CoinGecko free limit is ~30

interface CoinGeckoPrice {
  [key: string]: {
    usd: number;
    usd_24h_change?: number;
  };
}

// Map symbols to CoinGecko IDs
const SYMBOL_MAP: Record<string, string> = {
  'BTCUSDT': 'bitcoin',
  'ETHUSDT': 'ethereum',
  'SOLUSDT': 'solana',
  'ADAUSDT': 'cardano',
  'DOTUSDT': 'polkadot',
  'LINKUSDT': 'chainlink',
  'MATICUSDT': 'matic-network',
  'AVAXUSDT': 'avalanche-2',
  'ATOMUSDT': 'cosmos',
  'UNIUSDT': 'uniswap',
};

// Fallback/mock prices when API is rate limited
const FALLBACK_PRICES: Record<string, number> = {
  'BTCUSDT': 96500,
  'ETHUSDT': 2750,
  'SOLUSDT': 198,
  'ADAUSDT': 0.95,
  'DOTUSDT': 6.5,
  'LINKUSDT': 19.5,
  'MATICUSDT': 0.42,
  'AVAXUSDT': 35,
  'ATOMUSDT': 4.5,
  'UNIUSDT': 8.5,
};

function getCoinGeckoId(symbol: string): string | null {
  return SYMBOL_MAP[symbol] || null;
}

function checkRateLimit(): boolean {
  const now = Date.now();
  if (now > REQUEST_TRACKER.resetTime) {
    // Reset counter every minute
    REQUEST_TRACKER.count = 0;
    REQUEST_TRACKER.resetTime = now + 60000;
  }
  REQUEST_TRACKER.count++;
  return REQUEST_TRACKER.count <= MAX_REQUESTS_PER_MINUTE;
}

async function fetchPriceFromCoinGecko(symbol: string): Promise<{ price: number; source: string } | null> {
  // Check cache first
  const cached = priceCache.get(symbol);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return { price: cached.price, source: 'cache' };
  }

  const coinId = getCoinGeckoId(symbol);
  if (!coinId) {
    console.error(`Unknown symbol: ${symbol}`);
    return null;
  }

  // Check rate limit
  if (!checkRateLimit()) {
    console.warn(`Rate limit reached, using fallback for ${symbol}`);
    const fallbackPrice = FALLBACK_PRICES[symbol];
    if (fallbackPrice) {
      return { price: fallbackPrice, source: 'fallback' };
    }
    return null;
  }

  try {
    const response = await fetch(
      `https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd`,
      {
        headers: { 'Accept': 'application/json' },
        next: { revalidate: 0 }
      }
    );

    if (response.status === 429) {
      console.warn(`CoinGecko rate limit (429) for ${symbol}, using fallback`);
      const fallbackPrice = FALLBACK_PRICES[symbol];
      if (fallbackPrice) {
        return { price: fallbackPrice, source: 'fallback' };
      }
      return null;
    }

    if (!response.ok) {
      console.error(`CoinGecko API error for ${symbol}: ${response.status}`);
      const fallbackPrice = FALLBACK_PRICES[symbol];
      if (fallbackPrice) {
        return { price: fallbackPrice, source: 'fallback' };
      }
      return null;
    }

    const data: CoinGeckoPrice = await response.json();
    const price = data[coinId]?.usd;

    if (!price || isNaN(price)) {
      console.error(`Invalid price for ${symbol}: ${price}`);
      return null;
    }

    // Update cache
    priceCache.set(symbol, { price, timestamp: Date.now(), source: 'coingecko' });
    
    return { price, source: 'coingecko' };
  } catch (error) {
    console.error(`Failed to fetch price for ${symbol}:`, error);
    const fallbackPrice = FALLBACK_PRICES[symbol];
    if (fallbackPrice) {
      return { price: fallbackPrice, source: 'fallback' };
    }
    return null;
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const symbols = searchParams.get('symbols');

    if (!symbols) {
      return NextResponse.json(
        { error: 'Missing symbols parameter' },
        { status: 400 }
      );
    }

    const symbolList = symbols.split(',').map(s => s.trim().toUpperCase());
    const results: Record<string, { price: number | null; timestamp: number; source: string; error?: string }> = {};

    // Fetch all prices in parallel
    const pricePromises = symbolList.map(async (symbol) => {
      const result = await fetchPriceFromCoinGecko(symbol);
      results[symbol] = {
        price: result?.price || null,
        timestamp: Date.now(),
        source: result?.source || 'error',
        error: result === null ? 'Failed to fetch price' : undefined
      };
    });

    await Promise.all(pricePromises);

    return NextResponse.json({
      success: true,
      data: results,
      timestamp: Date.now()
    });

  } catch (error) {
    console.error('Price API Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch prices' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { symbols } = body;

    if (!symbols || !Array.isArray(symbols)) {
      return NextResponse.json(
        { error: 'Missing or invalid symbols array' },
        { status: 400 }
      );
    }

    const results: Record<string, { price: number | null; timestamp: number; source: string; error?: string }> = {};

    // Fetch all prices in parallel
    const pricePromises = symbols.map(async (symbol: string) => {
      const result = await fetchPriceFromCoinGecko(symbol.toUpperCase());
      results[symbol] = {
        price: result?.price || null,
        timestamp: Date.now(),
        source: result?.source || 'error',
        error: result === null ? 'Failed to fetch price' : undefined
      };
    });

    await Promise.all(pricePromises);

    return NextResponse.json({
      success: true,
      data: results,
      timestamp: Date.now()
    });

  } catch (error) {
    console.error('Price API Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch prices' },
      { status: 500 }
    );
  }
}
