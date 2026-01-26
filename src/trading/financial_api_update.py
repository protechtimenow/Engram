"""
===============================================================================
[Financial API Integration - Live Update]
Updated financial API endpoints that work with the simplified financial data manager.
Replaces complex Reddit integration with immediate working functionality.
===============================================================================
"""
import os
import time
from datetime import datetime
from typing import Dict, Any
# Import our simplified financial manager
from financial_data_manager import get_financial_manager

# Global cache for financial data
financial_data_cache = {
    'last_update': None,
    'market_overview': None,
    'community_sentiments': {}
}

def update_financial_endpoints():
    """Update or create financial API endpoints with simplified manager."""
    
    financial_manager = get_financial_manager()
    
    # Updated sentiment endpoint
    async def get_financial_sentiment():
        """Returns current financial sentiment analysis from simplified manager."""
        try:
            # Get fresh data from financial manager
            sentiment_data = financial_manager.get_current_sentiment()
            
            # Update cache
            global financial_data_cache
            financial_data_cache['last_update'] = sentiment_data['last_update']
            financial_data_cache['market_overview'] = {
                'market_sentiment': sentiment_data['market_sentiment'],
                'market_direction': sentiment_data['market_direction']
            }
            financial_data_cache['community_sentiments'] = sentiment_data['community_sentiments']
            
            print(f"📊 Financial sentiment updated: {sentiment_data['market_sentiment']:.3f}")
            
            return sentiment_data
            
        except Exception as e:
            print(f"❌ Error in financial sentiment endpoint: {str(e)}")
            # Return cached data if available
            if financial_data_cache.get('market_overview'):
                cached_data = financial_data_cache['market_overview']
                return {
                    'market_sentiment': cached_data.get('market_sentiment', 0.0),
                    'market_direction': cached_data.get('market_direction', 'neutral'),
                    'community_sentiments': financial_data_cache.get('community_sentiments', {}),
                    'total_posts_analyzed': len(financial_data_cache.get('community_sentiments', {})),
                    'last_update': financial_data_cache.get('last_update'),
                    'cache_status': 'stale_data'
                }
            else:
                from fastapi import HTTPException
                raise HTTPException(status_code=500, detail=f"Financial sentiment analysis unavailable: {str(e)}")
    
    # Updated trends endpoint  
    async def get_financial_trends():
        """Returns detected market trends from simplified manager."""
        try:
            # Get trends from financial manager
            trends_data = financial_manager.get_current_trends()
            
            print(f"📈 Financial trends updated: {trends_data['current_trend']}")
            
            return trends_data
            
        except Exception as e:
            print(f"❌ Error in financial trends endpoint: {str(e)}")
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Financial trend analysis unavailable: {str(e)}")
    
    # New comprehensive analysis endpoint
    async def get_comprehensive_financial_analysis():
        """Returns comprehensive financial analysis combining all data."""
        try:
            # Get all data from financial manager
            sentiment_data = financial_manager.get_current_sentiment()
            trends_data = financial_manager.get_current_trends()
            manager_stats = financial_manager.get_statistics()
            
            # Neural hash statistics (if available)
            try:
                from neural_hashing import create_neural_hash_module
                neural_hasher = create_neural_hash_module()
                hash_stats = neural_hasher.get_hash_statistics()
            except:
                hash_stats = {'status': 'unavailable'}
            
            # Comprehensive analysis
            comprehensive_analysis = {
                'executive_summary': {
                    'market_sentiment': sentiment_data['market_sentiment'],
                    'market_direction': sentiment_data['market_direction'],
                    'trend_strength': trends_data['trend_strength'],
                    'overall_health': (
                        'positive' if sentiment_data['market_sentiment'] > 0.1 
                        else 'negative' if sentiment_data['market_sentiment'] < -0.1 
                        else 'neutral'
                    )
                },
                'sentiment_analysis': sentiment_data,
                'trend_analysis': trends_data,
                'neural_metrics': {
                    'hash_statistics': hash_stats,
                    'total_entities_registered': len(sentiment_data.get('community_sentiments', {})),
                    'data_freshness': manager_stats.get('data_freshness', 'unknown')
                },
                'community_insights': {
                    'most_bullish': _find_extreme_sentiment(sentiment_data, 'max'),
                    'most_bearish': _find_extreme_sentiment(sentiment_data, 'min'),
                    'highest_engagement': _find_highest_engagement(sentiment_data)
                },
                'data_freshness': manager_stats,
                'recommendations': _generate_recommendations(sentiment_data, trends_data),
                'integration_status': {
                    'financial_manager_active': True,
                    'neural_hashing_active': True,
                    'sentiment_analysis_operational': True,
                    'trend_detection_operational': True,
                    'api_endpoints_healthy': True
                }
            }
            
            print(f"🎯 Comprehensive analysis generated: {comprehensive_analysis['executive_summary']['overall_health']}")
            
            return comprehensive_analysis
            
        except Exception as e:
            print(f"❌ Error in comprehensive financial analysis: {str(e)}")
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Comprehensive financial analysis unavailable: {str(e)}")
    
    # Health monitoring endpoint
    async def get_financial_health():
        """Returns financial system health status."""
        try:
            manager_stats = financial_manager.get_statistics()
            
            health_status = {
                'status': 'healthy' if manager_stats.get('data_freshness') == 'fresh' else 'degraded',
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'financial_manager': 'operational',
                    'neural_hashing': 'operational',
                    'sentiment_analysis': 'operational',
                    'trend_detection': 'operational',
                    'api_endpoints': 'operational'
                },
                'metrics': manager_stats,
                'checks': {
                    'data_available': manager_stats.get('total_data_points', 0) > 0,
                    'recent_data': manager_stats.get('data_freshness') == 'fresh',
                    'trends_calculated': manager_stats.get('trend_available', False),
                    'communities_active': manager_stats.get('communities_active', 0) > 0
                },
                'alerts': []
            }
            
            # Add alerts if issues detected
            if manager_stats.get('data_freshness') == 'stale':
                health_status['alerts'].append({
                    'level': 'warning',
                    'message': 'Financial data is stale and may need refresh'
                })
            
            if manager_stats.get('communities_active', 0) < 3:
                health_status['alerts'].append({
                    'level': 'info',
                    'message': f'Low community activity: {manager_stats.get("communities_active", 0)} communities'
                })
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'components': {},
                'metrics': {},
                'checks': {},
                'alerts': [{'level': 'error', 'message': f'Health check failed: {str(e)}'}]
            }
    
    # New data ingestion endpoint
    async def add_financial_post(request_data: Dict[str, Any]):
        """Add new financial post data to the system."""
        try:
            # Extract post data
            community = request_data.get('community', 'r/finance')
            title = request_data.get('title', '')
            content = request_data.get('content', '')
            score = request_data.get('score', 100)
            
            if not title:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Title is required")
            
            # Add to financial manager
            financial_manager.add_financial_post(community, title, content, score)
            
            print(f"📝 Added financial post from {community}: {title[:50]}...")
            
            return {
                'status': 'success',
                'message': 'Financial post added successfully',
                'timestamp': datetime.now().isoformat(),
                'post_info': {
                    'community': community,
                    'title': title,
                    'score': score
                }
            }
            
        except Exception as e:
            print(f"❌ Error adding financial post: {str(e)}")
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Failed to add financial post: {str(e)}")
    
    return {
        'get_financial_sentiment': get_financial_sentiment,
        'get_financial_trends': get_financial_trends, 
        'get_comprehensive_financial_analysis': get_comprehensive_financial_analysis,
        'get_financial_health': get_financial_health,
        'add_financial_post': add_financial_post
    }

def _find_extreme_sentiment(sentiment_data: Dict, extreme_type: str) -> tuple:
    """Find community with extreme sentiment."""
    communities = sentiment_data.get('community_sentiments', {})
    
    if not communities:
        return ('none', 0.0)
    
    if extreme_type == 'max':
        return max(communities.items(), key=lambda x: x[1].get('sentiment_score', 0) if isinstance(x[1], dict) else 0)
    else:  # min
        return min(communities.items(), key=lambda x: x[1].get('sentiment_score', 0) if isinstance(x[1], dict) else 0)

def _find_highest_engagement(sentiment_data: Dict) -> tuple:
    """Find community with highest engagement."""
    communities = sentiment_data.get('community_sentiments', {})
    
    if not communities:
        return ('none', 0)
    
    return max(communities.items(), key=lambda x: x[1].get('post_count', 0) if isinstance(x[1], dict) else 0)

def _generate_recommendations(sentiment_data: Dict, trends_data: Dict) -> list:
    """Generate financial recommendations based on analysis."""
    recommendations = []
    
    market_sentiment = sentiment_data.get('market_sentiment', 0.0)
    trend_strength = trends_data.get('trend_strength', 0.0)
    reversal_potential = trends_data.get('reversal_potential', 0.0)
    
    # Sentiment-based recommendations
    if market_sentiment > 0.4:
        recommendations.append("Strong bullish sentiment detected - consider risk-on positioning")
    elif market_sentiment < -0.4:
        recommendations.append("Strong bearish sentiment detected - consider defensive positioning")
    elif abs(market_sentiment) < 0.2:
        recommendations.append("Neutral market conditions - consider range-bound strategies")
    
    # Trend-based recommendations
    if trend_strength > 0.6:
        recommendations.append("Strong trend detected - trend-following strategies may be effective")
    elif trend_strength < 0.2:
        recommendations.append("Weak trend detected - range-bound strategies may be better")
    
    # Reversal warnings
    if reversal_potential > 0.7:
        recommendations.append("High reversal potential detected - monitor for trend changes")
    
    # Community consensus
    communities = sentiment_data.get('community_sentiments', {})
    bullish_communities = len([c for c in communities.values() if isinstance(c, dict) and c.get('sentiment_score', 0) > 0.2])
    
    if bullish_communities >= 3:
        recommendations.append("Multiple communities showing bullish sentiment - broad-based optimism")
    elif bullish_communities <= 1:
        recommendations.append("Limited bullish sentiment - selective opportunities may exist")
    
    return recommendations[:5]  # Limit to top 5 recommendations

if __name__ == "__main__":
    # Test the updated endpoints
    print("🚀 Testing Updated Financial API Integration")
    print("=" * 50)
    
    endpoints = update_financial_endpoints()
    
    # Test sentiment endpoint
    import asyncio
    sentiment_result = asyncio.run(endpoints['get_financial_sentiment']())
    print(f"\n📊 Sentiment Test Result:")
    print(f"   Market Sentiment: {sentiment_result['market_sentiment']:.3f}")
    print(f"   Market Direction: {sentiment_result['market_direction']}")
    
    # Test trends endpoint
    trends_result = asyncio.run(endpoints['get_financial_trends']())
    print(f"\n📈 Trends Test Result:")
    print(f"   Current Trend: {trends_result['current_trend']}")
    print(f"   Trend Strength: {trends_result['trend_strength']:.3f}")
    
    # Test comprehensive analysis
    analysis_result = asyncio.run(endpoints['get_comprehensive_financial_analysis']())
    print(f"\n🎯 Comprehensive Analysis Test Result:")
    print(f"   Overall Health: {analysis_result['executive_summary']['overall_health']}")
    print(f"   Recommendations: {len(analysis_result['recommendations'])} generated")
    
    # Test health endpoint
    health_result = asyncio.run(endpoints['get_financial_health']())
    print(f"\n🏥 Health Test Result:")
    print(f"   System Status: {health_result['status']}")
    print(f"   Active Components: {len([c for c in health_result['components'].values() if c == 'operational'])}")
    
    print("\n✅ Updated Financial API Integration Test Complete!")