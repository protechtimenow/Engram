"""
===============================================================================
[Engram + Clawdbot Unified Dashboard]
Complete integration dashboard that combines Engram financial neural capacity
with Clawdbot multi-channel AI agent capabilities.
Provides real-time monitoring, alert systems, and unified control interface.
===============================================================================
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from financial_data_manager import get_financial_manager
from clawdbot_integration import create_clawdbot_integration, ClawdbotChannel
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

class UnifiedDashboard:
    """
    Unified dashboard for Engram + Clawdbot integration.
    Provides real-time monitoring, alerts, and control interface.
    """
    
    def __init__(self):
        self.financial_manager = get_financial_manager()
        self.clawdbot = create_clawdbot_integration()
        self.start_time = time.time()
        
        print("🚀 Unified Dashboard initialized")
        print(f"   Financial Manager: {len(self.financial_manager.data_points)} data points")
        print(f"   Clawdbot Agents: {len(self.clawdbot.agents)} agents")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        
        # Financial sentiment data
        financial_sentiment = self.financial_manager.get_current_sentiment()
        financial_trends = self.financial_manager.get_current_trends()
        financial_stats = self.financial_manager.get_statistics()
        
        # Clawdbot agent data
        clawdbot_status = self.clawdbot.get_channel_status()
        clawdbot_insights = self.clawdbot.get_agent_insights()
        
        # Unified metrics
        unified_metrics = {
            'uptime_seconds': time.time() - self.start_time,
            'data_points_processed': len(self.financial_manager.data_points),
            'messages_processed': len(self.clawdbot.messages),
            'active_channels': len(self.clawdbot.active_channels),
            'system_health': 'operational' if self._check_system_health() else 'degraded'
        }
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'financial_analysis': {
                'sentiment': financial_sentiment,
                'trends': financial_trends,
                'statistics': financial_stats
            },
            'agent_network': {
                'status': clawdbot_status,
                'agents': clawdbot_insights,
                'total_agents': len(self.clawdbot.agents),
                'active_agents': len([a for a in self.clawdbot.agents.values() if a.status == 'active'])
            },
            'unified_metrics': unified_metrics,
            'integration_points': {
                'financial_neural_capacity': True,
                'multi_channel_agents': True,
                'sentiment_analysis': True,
                'alert_systems': True,
                'real_time_monitoring': True,
                'api_integration': True
            }
        }
        
        return dashboard_data
    
    def _check_system_health(self) -> bool:
        """Check overall system health."""
        try:
            # Check financial data freshness
            financial_stats = self.financial_manager.get_statistics()
            data_fresh = financial_stats.get('data_freshness') == 'fresh'
            
            # Check agent activity
            recent_agent_activity = any(
                time.time() - agent.last_active < 300 
                for agent in self.clawdbot.agents.values() 
                if agent.status == 'active'
            )
            
            # Check message processing
            recent_messages = len([
                m for m in self.clawdbot.messages 
                if time.time() - m.timestamp < 600
            ])
            
            return data_fresh and recent_agent_activity and recent_messages > 0
            
        except Exception:
            return False
    
    async def create_financial_alert(self, alert_type: str, **kwargs) -> bool:
        """Create unified financial alert."""
        
        # Format alert data
        alert_data = dict(kwargs)
        
        # Send via Clawdbot
        success = self.clawdbot.create_financial_alert(alert_type, alert_data)
        
        if success:
            # Also add to financial manager for historical tracking
            alert_summary = f"{alert_type}: {alert_data}"
            self.financial_manager.add_financial_post(
                community="r/SystemAlerts",
                title=alert_summary,
                content=json.dumps(alert_data),
                score=1000
            )
        
        return success
    
    def get_unified_status(self) -> Dict[str, Any]:
        """Get unified system status."""
        return {
            'system_status': 'operational' if self._check_system_health() else 'degraded',
            'components': {
                'financial_manager': 'operational',
                'clawdbot_integration': 'operational',
                'unified_dashboard': 'operational',
                'api_endpoints': 'operational'
            },
            'data_quality': {
                'financial_data_fresh': self.financial_manager.get_statistics().get('data_freshness') == 'fresh',
                'agent_data_current': any(
                    time.time() - agent.last_active < 300
                    for agent in self.clawdbot.agents.values()
                ),
                'message_processing_active': len([
                    m for m in self.clawdbot.messages 
                    if time.time() - m.timestamp < 600
                ]) > 0
            },
            'active_capabilities': [
                'sentiment_analysis',
                'trend_detection', 
                'entity_extraction',
                'multi_channel_messaging',
                'financial_alerts',
                'real_time_monitoring',
                'unified_dashboard'
            ]
        }

# Create FastAPI app for dashboard
dashboard_app = FastAPI(
    title="Engram + Clawdbot Unified Dashboard",
    description="Real-time financial analysis and AI agent monitoring"
)

# Enable CORS
dashboard_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize dashboard
unified_dashboard = UnifiedDashboard()

@dashboard_app.get("/")
async def dashboard_home():
    """Serve dashboard home page."""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Engram + Clawdbot Unified Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #ffffff; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #4CAF50; margin: 0; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: #2d3748; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .card h3 { color: #4CAF50; margin-top: 0; }
            .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
            .metric { text-align: center; }
            .metric-value { font-size: 24px; font-weight: bold; color: #4CAF50; }
            .metric-label { font-size: 14px; color: #ccc; }
            .status { padding: 10px; border-radius: 4px; margin: 5px 0; }
            .healthy { background: #4CAF50; color: white; }
            .degraded { background: #ff9800; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠🤖 Engram + Clawdbot Unified Dashboard</h1>
            </div>
            
            <div class="cards">
                <div class="card">
                    <h3>📊 Financial Analysis</h3>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value" id="market-sentiment">--</div>
                            <div class="metric-label">Market Sentiment</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" id="trend-strength">--</div>
                            <div class="metric-label">Trend Strength</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🤖 AI Agent Network</h3>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value" id="active-agents">--</div>
                            <div class="metric-label">Active Agents</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" id="total-messages">--</div>
                            <div class="metric-label">Messages Processed</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚡ System Health</h3>
                    <div class="status healthy" id="system-status">
                        System Status: Checking...
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Auto-refresh dashboard data
            async function updateDashboard() {
                try {
                    const response = await fetch('/api/dashboard/data');
                    const data = await response.json();
                    
                    // Update financial metrics
                    document.getElementById('market-sentiment').textContent = 
                        data.financial_analysis.sentiment.market_sentiment.toFixed(3);
                    
                    document.getElementById('trend-strength').textContent = 
                        data.financial_analysis.trends.trend_strength.toFixed(3);
                    
                    // Update agent metrics
                    document.getElementById('active-agents').textContent = 
                        data.agent_network.active_agents;
                    
                    document.getElementById('total-messages').textContent = 
                        data.agent_network.total_messages;
                    
                    // Update system status
                    const statusElement = document.getElementById('system-status');
                    statusElement.textContent = `System Status: ${data.system_status}`;
                    statusElement.className = `status ${data.system_status}`;
                    
                } catch (error) {
                    console.error('Dashboard update error:', error);
                }
            }
            
            // Update every 5 seconds
            setInterval(updateDashboard, 5000);
            updateDashboard(); // Initial load
        </script>
    </body>
    </html>
    """)

@dashboard_app.get("/api/dashboard/data")
async def get_dashboard_data():
    """API endpoint for dashboard data."""
    try:
        return await unified_dashboard.get_dashboard_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data error: {str(e)}")

@dashboard_app.post("/api/alert/create")
async def create_alert_endpoint(alert_request: dict):
    """Create financial alert endpoint."""
    try:
        alert_type = alert_request.get('alert_type')
        alert_data = {k: v for k, v in alert_request.items() if k != 'alert_type'}
        
        success = await unified_dashboard.create_financial_alert(alert_type, **alert_data)
        
        return {
            'status': 'success' if success else 'failed',
            'alert_type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'data': alert_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert creation failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Engram + Clawdbot Unified Dashboard")
    print("=" * 50)
    print("Dashboard available at: http://localhost:8001")
    print("API endpoints:")
    print("  GET / - Dashboard home")
    print("  GET /api/dashboard/data - Dashboard data")
    print("  POST /api/alert/create - Create financial alerts")
    print("=" * 50)
    
    uvicorn.run(
        dashboard_app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )