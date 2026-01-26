import os
import glob
import httpx
import subprocess
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pydantic import BaseModel
from typing import List, Optional
import argparse
import glob
import hashlib
import uvicorn
from short_conv_model import LlamaShortConv, ModelConfig, hash_text_to_id
import torch
import asyncio
from datetime import datetime
from financial_data_manager import get_financial_manager
from neural_hashing import create_neural_hash_module

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        # Expanded CSP to allow fonts from perplexity and other common sources for a smooth UI
        csp_rules = [
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://r2cdn.perplexity.ai",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com https://r2cdn.perplexity.ai",
            "img-src 'self' data: https:",
            "connect-src 'self' http://127.0.0.1:1234 http://127.0.0.1:8000 http://localhost:1234"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_rules)
        return response

app = FastAPI(title="Engram Intelligent Hub (GLM/Liquid Bridge)")

# Add CSP middleware
app.add_middleware(CSPMiddleware)

# Configuration
GLM_API_URLS = [
    "http://127.0.0.1:1234/v1/chat/completions",
    "http://172.17.128.1:1234/v1/chat/completions",
    "http://localhost:1234/v1/chat/completions"
]

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 500
    stream: Optional[bool] = False

class ToolRequest(BaseModel):
    command: str

def get_project_context():
    """Provides ONLY the core logic summary to the model."""
    try:
        with open("openspec/project.md", 'r') as file:
            return f"CORE LOGIC:\n{file.read().strip()}\n"
    except:
        return "CORE LOGIC: Engram Intelligent Hub - Neural context management.\n"

def get_neural_fingerprint():
    """Generates hashes for all files in the project for context anchoring."""
    files = glob.glob("**/*.py", recursive=True) + glob.glob("**/*.md", recursive=True)
    fingerprint = {}
    for f in files:
        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            # Generate a stable ID for the file
            token_id = hash_text_to_id(content)
            # Simulate the Neural Hashing logic
            fingerprint[f] = {
                "token_id": token_id,
                "label": f.split('/')[-1]
            }
    return fingerprint

# Initialize the model once
print("🧠 Initializing Engram Neural Core...")
model_cfg = ModelConfig()
engram_model = LlamaShortConv(model_cfg)
engram_model.eval()

# Initialize Financial Neural Capacity
# Initialize Financial & Clawdbot Integration
print("💰 Initializing Financial Neural Capacity...")
from financial_data_manager import get_financial_manager
from financial_api_update import update_financial_endpoints

financial_manager = get_financial_manager()
financial_endpoints = update_financial_endpoints()

print("✅ Financial Neural Capacity fully initialized")

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # Aggregating dynamic context
    context = get_project_context()
    
    # Hardened, zero-fluff system prompt
    system_prompt = (
        "STRICT MODE: You are the Engram Architect. "
        f"{context}"
        "DIRECTIONS: "
        "1. DO NOT greet the user. "
        "2. DO NOT repeat your context. "
        "3. Wait for technical tasks. "
        "4. Use /run [command] to execute code via OpenCode if needed."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    for m in request.messages:
        messages.append(m.dict())

    # We use the model specified in the request
    target_model = request.model
    api_timeout = getattr(app.state, "timeout", 30.0)
    trust_proxy = getattr(app.state, "trust_proxy", False)
    
    print(f"🎯 Target Model: {target_model} (Timeout: {api_timeout}s, ProxyBypass: {not trust_proxy})")

    last_error = "No endpoints tried"
    for url in GLM_API_URLS:
        try:
            payload = {
                "model": target_model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": request.max_tokens or 1000,
                "stream": False
            }
            
            print(f"📡 Requesting {target_model} at {url}...")
            
            async with httpx.AsyncClient(timeout=api_timeout, trust_env=trust_proxy) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success from {url}")
                    return result
                else:
                    last_error = f"HTTP {response.status_code} from {url}: {response.text}"
                    print(f"❌ {last_error}")
                    continue
                    
        except Exception as e:
            last_error = f"Connection error to {url}: {str(e)}"
            print(f"❌ {last_error}")
            continue

    print(f"🚨 All Reasoning Engine endpoints failed for {target_model}")
    raise HTTPException(status_code=500, detail=f"Reasoning Engine Error: {last_error}")

@app.post("/opencode/execute")
async def execute_command(req: ToolRequest):
    """Executes a command locally mirroring OpenCode functionality."""
    try:
        result = subprocess.run(
            req.command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30,
            cwd=os.getcwd()
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

# Serve frontend
if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static", html=True), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/static/index.html")

@app.get("/api/specs")
async def list_specs():
    """Returns a list of markdown files in the openspec directory."""
    try:
        spec_files = glob.glob("openspec/**/*.md", recursive=True)
        return [f.replace("\\", "/") for f in spec_files]
    except Exception as e:
        print(f"Error listing specs: {e}")
        return []

@app.get("/api/engram/fingerprint")
async def get_fingerprint():
    """Exposes the project's neural fingerprints to the Hub."""
    fingerprint = get_neural_fingerprint()
    
    # Add financial metadata if available
    if financial_data_cache['market_overview']:
        fingerprint['financial_context'] = {
            'market_sentiment': financial_data_cache['market_overview'].get('market_sentiment', 0.0),
            'market_direction': financial_data_cache['market_overview'].get('market_direction', 'neutral'),
            'last_update': financial_data_cache['last_update']
        }
    
    return fingerprint

@app.get("/api/engram/financial/sentiment")
async def get_financial_sentiment():
    """Returns current financial sentiment analysis."""
    return await financial_endpoints['get_financial_sentiment']()

@app.get("/api/engram/financial/trends") 
async def get_financial_trends():
    """Returns detected market trends and analysis."""
    return await financial_endpoints['get_financial_trends']()

@app.get("/api/engram/financial/analysis")
async def get_comprehensive_financial_analysis():
    """Returns comprehensive financial analysis including sentiment, trends, and predictions."""
    return await financial_endpoints['get_comprehensive_financial_analysis']()

@app.get("/health/financial")
async def get_financial_health():
    """Returns financial system health status."""
    return await financial_endpoints['get_financial_health']()

@app.post("/api/engram/financial/post")
async def add_financial_post(request: dict):
    """Add new financial post data to the system."""
    return await financial_endpoints['add_financial_post'](request)

# Add periodic financial data refresh
async def periodic_financial_update():
    """Periodically update financial data with mock live data."""
    while True:
        try:
            # Simulate new financial posts from different communities
            import random
            
            communities = ['r/Quant', 'r/wallstreetbets', 'r/ValueInvesting', 'r/Economics']
            community = random.choice(communities)
            
            # Generate realistic mock data
            sentiment_templates = [
                ('Algorithmic models show {} sentiment in tech sector', 0.65),
                ('{} momentum detected in cryptocurrency markets', 0.78),
                ('Fundamental analysis reveals {} opportunities', 0.34),
                ('Federal Reserve policy creates market {}', -0.42),
                ('Earnings season {} expectations', 0.56)
            ]
            
            title_template, base_sentiment = random.choice(sentiment_templates)
            sentiment_adj = random.choice(['strong', 'moderate', 'slight'])
            title = title_template.format(f'{sentiment_adj} bullish' if base_sentiment > 0 else 'bearish')
            
            content = f"Analysis from {community} community with detailed market insights."
            score = random.randint(50, 500)
            
            # Add to financial manager
            financial_manager.add_financial_post(community, title, content, score)
            
            print(f"🔄 Auto-added financial post from {community}: sentiment={base_sentiment:.2f}")
            
        except Exception as e:
            print(f"❌ Error in periodic financial update: {str(e)}")
        
        # Wait 5 minutes before next update
        await asyncio.sleep(300)

@app.on_event("startup")
async def startup_financial_tasks():
    """Start financial background tasks."""
    print("🚀 Starting Financial Neural Capacity background tasks...")
    
    # Start periodic financial data updates
    asyncio.create_task(periodic_financial_update())
    
    # Add some initial data
    initial_posts = [
        ('r/Quant', 'Neural networks detect bullish patterns in DeFi sector', 0.68),
        ('r/wallstreetbets', '🚀 ETH breakout confirmed! Diamond hands! 💎🙌', 0.85),
        ('r/ValueInvesting', 'Discounted cash flow analysis reveals value opportunities', 0.42),
        ('r/Economics', 'Inflation concerns impact market sentiment negatively', -0.35)
    ]
    
    for community, title, sentiment in initial_posts:
        financial_manager.add_financial_post(community, title, f"Analysis from {community}", sentiment * 100)
    
    print("✅ Financial Neural Capacity fully initialized and operational")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Engram Hub Server")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds")
    parser.add_argument("--proxy-bypass", type=str, default="true", help="Whether to bypass system proxies (true/false)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    app.state.timeout = args.timeout
    app.state.trust_proxy = args.proxy_bypass.lower() != "true"

    print(f"🚀 Engram Hub Multi-Model Bridge ready.")
    print(f"🔗 Hub Dashboard: http://{args.host}:8000")
    print(f"⚙️ Config: Timeout={app.state.timeout}s, ProxyBypass={not app.state.trust_proxy}")
    uvicorn.run(app, host=args.host, port=8000)
