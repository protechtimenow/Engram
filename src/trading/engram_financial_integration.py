"""
===============================================================================
[Engram Server Financial Integration - Working Implementation]

Updated engram_server.py with working financial API endpoints
that use the simplified financial data manager for immediate functionality.
===============================================================================
"""

# Add these imports to engram_server.py:
from financial_data_manager import get_financial_manager
from financial_api_update import update_financial_endpoints

# Add this code after the existing API endpoints in engram_server.py:

# Financial Data Manager Initialization
financial_manager = get_financial_manager()

# Financial API Endpoints
financial_endpoints = update_financial_endpoints()

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

# Update the existing fingerprint endpoint to include financial context
@app.get("/api/engram/fingerprint")
async def get_fingerprint():
    """Exposes project's neural fingerprints with financial context."""
    fingerprint = get_neural_fingerprint()
    
    # Add financial context from financial manager
    try:
        sentiment_data = financial_manager.get_current_sentiment()
        fingerprint['financial_context'] = {
            'market_sentiment': sentiment_data['market_sentiment'],
            'market_direction': sentiment_data['market_direction'],
            'last_update': sentiment_data['last_update'],
            'total_posts_analyzed': sentiment_data['total_posts_analyzed']
        }
    except Exception as e:
        print(f"Error adding financial context to fingerprint: {str(e)}")
        fingerprint['financial_context'] = {'error': 'financial_context_unavailable'}
    
    return fingerprint

# Add periodic financial data refresh
async def periodic_financial_update():
    """Periodically update financial data with mock live data."""
    while True:
        try:
            # Simulate new financial posts from different communities
            import random
            import time
            
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

# Start periodic update task when server starts
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

"""
Add this to your main block in engram_server.py:

    # Start financial background task
    asyncio.create_task(startup_financial_tasks())
"""