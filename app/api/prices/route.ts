import { NextRequest, NextResponse } from "next/server";

// Cache for price data (5 second TTL)
const priceCache = new Map<string, { price: number; timestamp: number }>();
const CACHE_TTL = 5000; // 5 seconds cache TTL

interface CoinGeckoPrice {
  [key: string]: {
    usd: number;
    usd_24h_change?: number;
  };
}

// Map Binance symbols to CoinGecko IDs
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

function getCoinGeckoId(symbol: string): string | null {
  // Remove USDT suffix and look up
  const baseSymbol = symbol.replace('USDT', '');
  const id = SYMBOL_MAP[symbol] || SYMBOL_MAP[`${baseSymbol}USDT`];
  return id;
}

async function fetchPriceFromCoinGecko(symbol: string): Promise<number | null> {
  // Check cache first
  const cached = priceCache.get(symbol);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.price;
  }

  const coinId = getCoinGeckoId(symbol);
  if (!coinId) {
    console.error(`Unknown symbol: ${symbol}`);
    return null;
  }

  try {
    // Call CoinGecko API (free, no auth required)
    const response = await fetch(
      `https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd&include_24hr_change=true`,
      {
        headers: { 'Accept': 'application/json' },
        next: { revalidate: 0 }
      }
    );

    if (!response.ok) {
      console.error(`CoinGecko API error for ${symbol}: ${response.status}`);
      return null;
    }

    const data: CoinGeckoPrice = await response.json();
    const price = data[coinId]?.usd;

    if (!price || isNaN(price)) {
      console.error(`Invalid price for ${symbol}: ${price}`);
      return null;
    }

    // Update cache
    priceCache.set(symbol, { price, timestamp: Date.now() });
    
    return price;
  } catch (error) {
    console.error(`Failed to fetch price for ${symbol}:`, error);
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
    const results: Record<string, { price: number | null; timestamp: number; error?: string }> = {};

    // Fetch all prices in parallel
    const pricePromises = symbolList.map(async (symbol) => {
      const price = await fetchPriceFromCoinGecko(symbol);
      results[symbol] = {
        price,
        timestamp: Date.now(),
        error: price === null ? 'Failed to fetch price' : undefined
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

    const results: Record<string, { price: number | null; timestamp: number; error?: string }> = {};

    // Fetch all prices in parallel
    const pricePromises = symbols.map(async (symbol: string) => {
      const price = await fetchPriceFromCoinGecko(symbol.toUpperCase());
      results[symbol] = {
        price,
        timestamp: Date.now(),
        error: price === null ? 'Failed to fetch price' : undefined
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
