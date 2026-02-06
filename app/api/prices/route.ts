import { NextRequest, NextResponse } from "next/server";

// Cache for price data (5 second TTL)
const priceCache = new Map<string, { price: number; timestamp: number }>();
const CACHE_TTL = 5000; // 5 seconds

interface BinancePrice {
  symbol: string;
  price: string;
}

async function fetchPriceFromBinance(symbol: string): Promise<number | null> {
  // Check cache first
  const cached = priceCache.get(symbol);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.price;
  }

  try {
    // Call Binance API directly
    const response = await fetch(`https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`, {
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      console.error(`Binance API error for ${symbol}: ${response.status}`);
      return null;
    }

    const data: BinancePrice = await response.json();
    const price = parseFloat(data.price);

    if (isNaN(price)) {
      console.error(`Invalid price for ${symbol}: ${data.price}`);
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
      const price = await fetchPriceFromBinance(symbol);
      results[symbol] = {
        price,
        timestamp: Date.now()
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
      const price = await fetchPriceFromBinance(symbol.toUpperCase());
      results[symbol] = {
        price,
        timestamp: Date.now()
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
