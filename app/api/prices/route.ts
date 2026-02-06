import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import * as path from "path";

const execAsync = promisify(exec);
const SCRIPTS_DIR = path.join(process.cwd(), "src", "engram", "scripts");

// Cache for price data (5 second TTL)
const priceCache = new Map<string, { price: number; timestamp: number }>();
const CACHE_TTL = 5000; // 5 seconds

async function fetchPrice(symbol: string): Promise<number | null> {
  // Check cache first
  const cached = priceCache.get(symbol);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.price;
  }

  try {
    const scriptPath = path.join(SCRIPTS_DIR, "fetch_data.py");
    const { stdout } = await execAsync(
      `python "${scriptPath}" --pair ${symbol} --output json`,
      { timeout: 10000 }
    );

    // Parse JSON from stdout (skip progress messages)
    const lines = stdout.trim().split('\n');
    const jsonStart = lines.findIndex(l => l.trim().startsWith('{'));
    
    if (jsonStart === -1) return null;
    
    const jsonStr = lines.slice(jsonStart).join('\n');
    const data = JSON.parse(jsonStr);
    const price = data.current_price;

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

    // Fetch all prices (could be parallelized for better performance)
    for (const symbol of symbolList) {
      const price = await fetchPrice(symbol);
      results[symbol] = {
        price,
        timestamp: Date.now()
      };
    }

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

    for (const symbol of symbols) {
      const price = await fetchPrice(symbol.toUpperCase());
      results[symbol] = {
        price,
        timestamp: Date.now()
      };
    }

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
