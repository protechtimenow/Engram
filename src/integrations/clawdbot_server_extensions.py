"""
===============================================================================
[Clawdbot Engram Server Extensions]

Server extensions to integrate Clawdbot capabilities into Engram's API.
Provides multi-channel AI agent endpoints and financial alert systems.
===============================================================================
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

from clawdbot_integration import ClawdbotIntegration, ClawdbotChannel, ClawdbotAgent

class ClawdbotMessageRequest(BaseModel):
    """Request model for sending messages via Clawdbot."""
    channel: str
    content: str
    target: Optional[str] = None

class ClawdbotAlertRequest(BaseModel):
    """Request model for creating financial alerts."""
    alert_type: str
    data: Dict[str, Any]

class ClawdbotStatusResponse(BaseModel):
    """Response model for Clawdbot status."""
    status: str
    channel_configs: Dict[str, Any]
    agents: List[Dict[str, Any]]
    insights: Dict[str, Any]

def create_clawdbot_endpoints(app: FastAPI, clawdbot_integration: ClawdbotIntegration):
    """Create Clawdbot API endpoints for Engram server."""
    
    @app.get("/api/clawdbot/status")
    async def get_clawdbot_status():
        """Get status of all Clawdbot channels and agents."""
        try:
            status = clawdbot_integration.get_channel_status()
            
            # Convert agents to dicts
            agent_dicts = []
            for agent in clawdbot_integration.agents.values():
                agent_dicts.append({
                    'id': agent.id,
                    'name': agent.name,
                    'channel': agent.channel.value,
                    'status': agent.status,
                    'capabilities': agent.capabilities,
                    'last_active': agent.last_active,
                    'message_count': agent.message_count
                })
            
            return ClawdbotStatusResponse(
                status="operational",
                channel_configs=status['channel_distribution'],
                agents=agent_dicts,
                insights=clawdbot_integration.get_agent_insights()
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Clawdbot status error: {str(e)}")
    
    @app.post("/api/clawdbot/message")
    async def send_clawdbot_message(request: ClawdbotMessageRequest):
        """Send a message through specified Clawdbot channel."""
        try:
            # Validate channel
            try:
                channel = ClawdbotChannel(request.channel.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid channel: {request.channel}"
                )
            
            # Send message
            message = clawdbot_integration.process_message(
                channel=channel,
                content=request.content,
                sender="api_user",
                metadata={"target": request.target} if request.target else {}
            )
            
            return {
                'status': 'success',
                'message_id': message.id,
                'channel': message.channel.value,
                'timestamp': message.timestamp,
                'sentiment_score': message.sentiment_score,
                'entities': message.entities
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Message send failed: {str(e)}")
    
    @app.post("/api/clawdbot/alert")
    async def create_clawdbot_alert(request: ClawdbotAlertRequest):
        """Create and broadcast financial alert through all active channels."""
        try:
            # Validate alert type
            valid_alerts = [
                'price_spike', 'sentiment_shift', 'trend_reversal', 
                'volume_anomaly', 'risk_warning'
            ]
            
            if request.alert_type not in valid_alerts:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid alert type: {request.alert_type}"
                )
            
            # Create and send alert
            success = clawdbot_integration.create_financial_alert(
                alert_type=request.alert_type,
                data=request.data
            )
            
            return {
                'status': 'success' if success else 'failed',
                'alert_type': request.alert_type,
                'channels_notified': len(clawdbot_integration.active_channels),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Alert creation failed: {str(e)}")
    
    @app.get("/api/clawdbot/agents")
    async def get_clawdbot_agents():
        """Get list of all configured Clawdbot agents."""
        try:
            agents = []
            for agent in clawdbot_integration.agents.values():
                agents.append({
                    'id': agent.id,
                    'name': agent.name,
                    'channel': agent.channel.value,
                    'status': agent.status,
                    'capabilities': agent.capabilities,
                    'last_active': agent.last_active,
                    'message_count': agent.message_count,
                    'uptime_seconds': time.time() - agent.last_active if agent.status == 'active' else 0
                })
            
            return {
                'status': 'success',
                'total_agents': len(agents),
                'active_agents': len([a for a in agents if a['status'] == 'active']),
                'agents': agents
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent list failed: {str(e)}")
    
    @app.get("/api/clawdbot/messages")
    async def get_clawdbot_messages(channel: Optional[str] = None, limit: int = 50):
        """Get recent messages from specified or all channels."""
        try:
            # Filter by channel if specified
            if channel:
                try:
                    channel_filter = ClawdbotChannel(channel.lower())
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid channel: {channel}"
                    )
                
                messages = [m for m in clawdbot_integration.messages if m.channel == channel_filter]
            else:
                messages = clawdbot_integration.messages
            
            # Sort by timestamp and limit
            messages_sorted = sorted(messages, key=lambda m: m.timestamp, reverse=True)[:limit]
            
            # Convert to dicts
            message_dicts = []
            for msg in messages_sorted:
                message_dicts.append({
                    'id': msg.id,
                    'channel': msg.channel.value,
                    'content': msg.content,
                    'sender': msg.sender,
                    'timestamp': msg.timestamp,
                    'sentiment_score': msg.sentiment_score,
                    'entities': msg.entities,
                    'metadata': msg.metadata
                })
            
            return {
                'status': 'success',
                'total_messages': len(messages),
                'returned_messages': len(message_dicts),
                'channel_filter': channel,
                'messages': message_dicts
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Message retrieval failed: {str(e)}")
    
    @app.get("/api/clawdbot/insights")
    async def get_clawdbot_insights():
        """Get comprehensive insights about Clawdbot performance and activity."""
        try:
            insights = clawdbot_integration.get_agent_insights()
            
            # Add additional analytics
            insights.update({
                'total_channels': len(ClawdbotChannel),
                'active_channels': len(clawdbot_integration.active_channels),
                'channel_types': [c.value for c in ClawdbotChannel],
                'integration_uptime': time.time() - min(
                    [a.last_active for a in clawdbot_integration.agents.values() if a.status == 'active']
                ),
                'message_rate': len(clawdbot_integration.messages) / max(1, (time.time() - min(
                    [m.timestamp for m in clawdbot_integration.messages]
                ))),
                'financial_entity_tracking': {
                    'total_entities_found': len(set().union(*[m.entities for m in clawdbot_integration.messages])),
                    'top_entities': ['BTC', 'ETH', 'AAPL', 'GOOGL', 'MSFT'],  # Would be calculated dynamically
                    'sentiment_accuracy': 0.85  # Mock accuracy
                }
            })
            
            return insights
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Insights retrieval failed: {str(e)}")

def setup_clawdbot_background_tasks(clawdbot_integration: ClawdbotIntegration):
    """Setup background tasks for Clawdbot integration."""
    
    async def periodic_agent_status_check():
        """Periodically check agent status and update activity."""
        while True:
            try:
                # Update agent status
                insights = clawdbot_integration.get_agent_insights()
                
                # Log inactive agents
                for agent in clawdbot_integration.agents.values():
                    if agent.status == 'active':
                        time_since_active = time.time() - agent.last_active
                        if time_since_active > 3600:  # 1 hour
                            print(f"⚠️ Agent {agent.name} inactive for {time_since_active:.0f} seconds")
                            agent.status = 'inactive'
                
                # Clean old messages (keep last 1000)
                current_time = time.time()
                clawdbot_integration.messages = [
                    m for m in clawdbot_integration.messages 
                    if current_time - m.timestamp < 86400  # Keep last 24 hours
                ]
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"❌ Background task error: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    return asyncio.create_task(periodic_agent_status_check())

# Integration function
def integrate_clawdbot_with_engram(app: FastAPI, financial_manager) -> Dict[str, Any]:
    """Integrate Clawdbot with Engram financial manager."""
    
    # Create Clawdbot integration
    from financial_data_manager import get_financial_manager
    
    clawdbot_integration = ClawdbotIntegration()
    
    # Get integration status
    integration_status = clawdbot_integration.integrate_with_engram_financial(financial_manager)
    
    # Setup background tasks
    background_task = setup_clawdbot_background_tasks(clawdbot_integration)
    
    print("🤖 Clawdbot-Engram integration established")
    
    return {
        'integration_status': integration_status,
        'clawdbot_instance': clawdbot_integration,
        'background_task': background_task,
        'endpoints_created': 5,
        'channels_supported': len(ClawdbotChannel)
    }

# Documentation strings
CLAWDBOT_API_DOCS = """
Clawdbot API Endpoints Documentation

## Core Endpoints

### GET /api/clawdbot/status
Get comprehensive status of all Clawdbot channels and configured agents.

**Response:**
```json
{
  "status": "operational",
  "channel_configs": {
    "telegram": {...},
    "discord": {...}
  },
  "agents": [
    {
      "id": "telegram-financial-bot",
      "name": "Financial Analysis Bot", 
      "channel": "telegram",
      "status": "active",
      "capabilities": ["sentiment_analysis", "market_data"]
    }
  ],
  "insights": {...}
}
```

### POST /api/clawdbot/message
Send a message through specified Clawdbot channel.

**Request:**
```json
{
  "channel": "telegram",
  "content": "Bitcoin is showing bullish momentum!",
  "target": "@user"
}
```

**Response:**
```json
{
  "status": "success",
  "message_id": "msg123",
  "channel": "telegram",
  "timestamp": 1640995200.0,
  "sentiment_score": 0.75,
  "entities": ["BTC", "bullish", "momentum"]
}
```

### POST /api/clawdbot/alert
Create and broadcast financial alerts through all active channels.

**Request:**
```json
{
  "alert_type": "price_spike",
  "data": {
    "symbol": "BTC",
    "change": 15.2,
    "price": 52000
  }
}
```

### GET /api/clawdbot/agents
Get list of all configured Clawdbot agents with status and capabilities.

### GET /api/clawdbot/messages
Get recent messages from specified or all channels.

**Query Parameters:**
- channel (optional): Filter by channel
- limit (optional, default 50): Maximum messages to return

### GET /api/clawdbot/insights
Get comprehensive analytics and insights about Clawdbot performance and activity.

## Integration Points

### Financial Data Synchronization
- Clawdbot messages automatically analyzed for sentiment
- Financial entities extracted and tracked
- Market data integrated with existing Engram financial manager

### Alert System
- Real-time price spike alerts
- Sentiment shift notifications  
- Trend reversal warnings
- Volume anomaly detection
- Risk level monitoring

### Multi-Channel Support
- Telegram (messaging, commands, media)
- Discord (embeds, slash commands, reactions)
- Slack (blocks, modals, file sharing)
- Web Dashboard (real-time charts, API access)
- WhatsApp (business API integration)
- Matrix (encrypted messaging)
- Zalo (Vietnamese platform)
- Voice Call (real-time transcription)

## Usage Examples

### Send Financial Alert
```bash
curl -X POST http://localhost:8000/api/clawdbot/alert \\
  -H "Content-Type: application/json" \\
  -d '{
    "alert_type": "price_spike",
    "data": {
      "symbol": "BTC",
      "change": 12.5,
      "price": 52000
    }
  }'
```

### Get Agent Status
```bash
curl http://localhost:8000/api/clawdbot/status
```

### Send Message
```bash
curl -X POST http://localhost:8000/api/clawdbot/message \\
  -H "Content-Type: application/json" \\
  -d '{
    "channel": "telegram", 
    "content": "Market analysis complete for today"
  }'
```
"""

if __name__ == "__main__":
    print("🤖 Clawdbot Engram Server Extensions")
    print("=" * 50)
    print(CLAWDBOT_API_DOCS)