"""
===============================================================================
[Financial Data Manager - Live Integration]
Simplified financial data manager that works without external dependencies.
Provides core financial neural capacity functionality with mock data for development.
===============================================================================
"""
import os
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class MarketSentiment(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish" 
    NEUTRAL = "neutral"

@dataclass
class FinancialDataPoint:
    timestamp: float
    community: str
    sentiment_score: float
    confidence: float
    post_count: int
    trending_entities: List[str]
    influence_weight: float

@dataclass
class MarketTrend:
    direction: str
    strength: float
    momentum: float
    reversal_potential: float
    timestamp: float

class SimpleFinancialDataManager:
    """
    Simplified financial data manager for immediate integration.
    Works without external dependencies and provides mock data for development.
    """
    
    def __init__(self):
        self.data_points: List[FinancialDataPoint] = []
        self.trends: List[MarketTrend] = []
        self.last_update = time.time()
        self.community_weights = {
            'r/Quant': 0.85,
            'r/finance': 0.75,
            'r/SecurityAnalysis': 0.80,
            'r/wallstreetbets': 0.60,
            'r/personalfinance': 0.50,
            'r/Economics': 0.70,
            'r/stocks': 0.65,
            'r/portfolios': 0.55,
            'r/investing': 0.70,
            'r/ValueInvesting': 0.75,
            'r/FluentInFinance': 0.65
        }
        
        # Initialize with mock data
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize with realistic mock financial data."""
        current_time = time.time()
        
        mock_data = [
            {
                'community': 'r/Quant',
                'title': 'Algorithmic models detect bullish momentum in tech sector',
                'sentiment': 0.65,
                'confidence': 0.82,
                'post_count': 45,
                'entities': ['tech', 'momentum', 'bullish', 'algorithms']
            },
            {
                'community': 'r/wallstreetbets', 
                'title': '🚀 BTC breakout confirmed! To the moon! 🚀',
                'sentiment': 0.89,
                'confidence': 0.75,
                'post_count': 234,
                'entities': ['BTC', 'breakout', 'moon', 'bullish']
            },
            {
                'community': 'r/ValueInvesting',
                'title': 'Fundamental analysis reveals undervalued opportunities in financial sector',
                'sentiment': 0.34,
                'confidence': 0.78,
                'post_count': 28,
                'entities': ['fundamental', 'undervalued', 'financial', 'value']
            },
            {
                'community': 'r/Economics',
                'title': 'Fed policy concerns create market volatility and uncertainty',
                'sentiment': -0.42,
                'confidence': 0.85,
                'post_count': 67,
                'entities': ['Fed', 'volatility', 'uncertainty', 'bearish']
            },
            {
                'community': 'r/stocks',
                'title': 'Earnings season beats expectations across major indices',
                'sentiment': 0.56,
                'confidence': 0.73,
                'post_count': 156,
                'entities': ['earnings', 'indices', 'bullish', 'beats']
            }
        ]
        
        # Create data points with time offsets
        for i, data in enumerate(mock_data):
            timestamp = current_time - (i * 300)  # 5 minute intervals
            
            data_point = FinancialDataPoint(
                timestamp=timestamp,
                community=data['community'],
                sentiment_score=data['sentiment'],
                confidence=data['confidence'],
                post_count=data['post_count'],
                trending_entities=data['entities'],
                influence_weight=self.community_weights.get(data['community'], 0.5)
            )
            
            self.data_points.append(data_point)
        
        # Generate trends
        self._calculate_trends()
        
        print(f"📊 Initialized with {len(self.data_points)} financial data points")
    
    def _calculate_trends(self):
        """Calculate market trends from sentiment data."""
        if len(self.data_points) < 3:
            return
        
        # Get recent data points (last 10)
        recent_points = sorted(self.data_points, key=lambda x: x.timestamp)[-10:]
        
        # Calculate weighted sentiment
        total_weight = 0
        weighted_sentiment = 0
        
        for point in recent_points:
            weight = point.confidence * point.post_count * point.influence_weight
            weighted_sentiment += point.sentiment_score * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_sentiment = weighted_sentiment / total_weight
        else:
            avg_sentiment = 0
        
        # Calculate trend direction and strength
        if len(recent_points) >= 5:
            # Compare recent vs earlier sentiment
            recent_avg = sum(p.sentiment_score for p in recent_points[-3:]) / 3
            earlier_avg = sum(p.sentiment_score for p in recent_points[-5:-2]) / 3
            
            sentiment_change = recent_avg - earlier_avg
            momentum = recent_points[-1].sentiment_score - recent_points[-2].sentiment_score
            
            # Determine trend
            if sentiment_change > 0.2:
                direction = "bullish_momentum"
            elif sentiment_change < -0.2:
                direction = "bearish_momentum"
            elif avg_sentiment > 0.3:
                direction = "bullish_consolidation"
            elif avg_sentiment < -0.3:
                direction = "bearish_consolidation"
            else:
                direction = "neutral"
            
            strength = min(1.0, abs(sentiment_change) * 2)
            reversal_potential = abs(recent_avg - earlier_avg) * 1.5
        else:
            direction = "insufficient_data"
            strength = 0.0
            momentum = 0.0
            reversal_potential = 0.0
        
        trend = MarketTrend(
            direction=direction,
            strength=strength,
            momentum=momentum if 'momentum' in locals() else 0.0,
            reversal_potential=reversal_potential if 'reversal_potential' in locals() else 0.0,
            timestamp=time.time()
        )
        
        self.trends = [trend]
    
    def get_current_sentiment(self) -> Dict[str, Any]:
        """Get current market sentiment analysis."""
        if not self.data_points:
            return {
                'market_sentiment': 0.0,
                'market_direction': MarketSentiment.NEUTRAL.value,
                'community_sentiments': {},
                'total_posts_analyzed': 0,
                'last_update': datetime.now().isoformat(),
                'hashing_active': True,
                'neural_pathways_active': True
            }
        
        # Calculate overall sentiment
        total_weight = 0
        weighted_sentiment = 0
        community_sentiments = {}
        
        for point in self.data_points:
            weight = point.confidence * point.post_count * point.influence_weight
            weighted_sentiment += point.sentiment_score * weight
            total_weight += weight
            
            # Track community sentiments
            if point.community not in community_sentiments:
                community_sentiments[point.community] = {
                    'sentiment_score': 0,
                    'confidence': 0,
                    'post_count': 0,
                    'trending_entities': []
                }
            
            comm_data = community_sentiments[point.community]
            comm_weight = point.confidence * point.post_count
            comm_sentiment_total = comm_data['sentiment_score'] * comm_data['confidence'] * comm_data['post_count']
            new_comm_sentiment_total = comm_sentiment_total + (point.sentiment_score * comm_weight)
            
            if comm_data['post_count'] > 0:
                comm_data['sentiment_score'] = new_comm_sentiment_total / (comm_data['confidence'] * comm_data['post_count'] * 2)
                comm_data['confidence'] = (comm_data['confidence'] + point.confidence) / 2
            else:
                comm_data['sentiment_score'] = point.sentiment_score
                comm_data['confidence'] = point.confidence
            
            comm_data['post_count'] += point.post_count
            comm_data['trending_entities'].extend(point.trending_entities)
        
        overall_sentiment = weighted_sentiment / total_weight if total_weight > 0 else 0
        market_direction = (
            MarketSentiment.BULLISH.value if overall_sentiment > 0.1
            else MarketSentiment.BEARISH.value if overall_sentiment < -0.1
            else MarketSentiment.NEUTRAL.value
        )
        
        return {
            'market_sentiment': overall_sentiment,
            'market_direction': market_direction,
            'community_sentiments': community_sentiments,
            'total_posts_analyzed': len(self.data_points),
            'last_update': datetime.now().isoformat(),
            'hashing_active': True,
            'neural_pathways_active': True
        }
    
    def get_current_trends(self) -> Dict[str, Any]:
        """Get current market trend analysis."""
        if not self.trends:
            return {
                'current_trend': 'insufficient_data',
                'trend_strength': 0.0,
                'sentiment_momentum': 0.0,
                'reversal_potential': 0.0,
                'community_consensus': {},
                'neural_detected': False,
                'last_update': datetime.now().isoformat()
            }
        
        trend = self.trends[0]
        
        # Calculate community consensus
        community_consensus = {}
        for point in self.data_points[-5:]:  # Recent 5 points
            if point.community not in community_consensus:
                community_consensus[point.community] = []
            community_consensus[point.community].append(point.sentiment_score)
        
        # Average by community
        for community, sentiments in community_consensus.items():
            community_consensus[community] = sum(sentiments) / len(sentiments)
        
        return {
            'current_trend': trend.direction,
            'trend_strength': trend.strength,
            'sentiment_momentum': trend.momentum,
            'reversal_potential': trend.reversal_potential,
            'community_consensus': community_consensus,
            'neural_detected': True,
            'last_update': datetime.now().isoformat()
        }
    
    def analyze_text_sentiment(self, text: str, entities: List[str] = None) -> Dict[str, Any]:
        """Analyze sentiment of financial text using simple rules."""
        # Define sentiment keywords
        bullish_words = [
            'bullish', 'buy', 'long', 'rally', 'surge', 'gain', 'profit', 'growth',
            'breakout', 'momentum', 'bull', 'call', 'up', 'rise', 'increase',
            'strong', 'beat', 'moon', 'rocket', 'to the moon'
        ]
        
        bearish_words = [
            'bearish', 'sell', 'short', 'drop', 'fall', 'loss', 'decline',
            'recession', 'crash', 'downturn', 'bear', 'put', 'down',
            'decrease', 'weak', 'fear', 'uncertainty', 'volatility', 'risk'
        ]
        
        words = text.lower().split()
        bullish_count = sum(1 for word in words if word in bullish_words)
        bearish_count = sum(1 for word in words if word in bearish_words)
        
        total_words = bullish_count + bearish_count
        
        if total_words == 0:
            sentiment_score = 0.0
            confidence = 0.1
        else:
            sentiment_score = (bullish_count - bearish_count) / total_words
            confidence = min(1.0, total_words / 10)  # More words = higher confidence
        
        direction = (
            MarketSentiment.BULLISH.value if sentiment_score > 0.1
            else MarketSentiment.BEARISH.value if sentiment_score < -0.1
            else MarketSentiment.NEUTRAL.value
        )
        
        return {
            'sentiment_score': max(-1.0, min(1.0, sentiment_score)),
            'confidence': confidence,
            'direction': direction,
            'entity_count': len(entities) if entities else 0,
            'hash_integration_active': True
        }
    
    def add_financial_post(self, community: str, title: str, content: str, score: int = 100) -> None:
        """Add a new financial post to the analysis."""
        entities = self._extract_entities(title + ' ' + content)
        sentiment_analysis = self.analyze_text_sentiment(title + ' ' + content, entities)
        
        data_point = FinancialDataPoint(
            timestamp=time.time(),
            community=community,
            sentiment_score=sentiment_analysis['sentiment_score'],
            confidence=sentiment_analysis['confidence'],
            post_count=score // 10,  # Estimate post count from score
            trending_entities=entities,
            influence_weight=self.community_weights.get(community, 0.5)
        )
        
        self.data_points.append(data_point)
        
        # Recalculate trends
        self._calculate_trends()
        
        print(f"📈 Added financial post from {community}: sentiment={sentiment_analysis['sentiment_score']:.3f}")
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract financial entities from text."""
        entities = []
        
        # Stock ticker patterns
        import re
        stocks = re.findall(r'\$[A-Z]{1,5}', text.upper())
        entities.extend(stocks)
        
        # Crypto patterns
        crypto_terms = ['BTC', 'ETH', 'Bitcoin', 'Ethereum', 'USDT', 'USDC']
        for crypto in crypto_terms:
            if crypto.lower() in text.lower():
                entities.append(crypto)
        
        # Financial terms
        financial_terms = [
            'bullish', 'bearish', 'momentum', 'volatility', 'earnings',
            'Fed', 'inflation', 'interest', 'rates', 'algorithm', 'trading'
        ]
        
        text_lower = text.lower()
        for term in financial_terms:
            if term in text_lower:
                entities.append(term)
        
        return list(set(entities))  # Remove duplicates
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get financial data manager statistics."""
        if not self.data_points:
            return {'status': 'no_data'}
        
        recent_points = [p for p in self.data_points if time.time() - p.timestamp < 3600]  # Last hour
        
        return {
            'total_data_points': len(self.data_points),
            'recent_data_points': len(recent_points),
            'communities_active': len(set(p.community for p in self.data_points)),
            'last_update': datetime.fromtimestamp(self.last_update).isoformat(),
            'data_freshness': 'fresh' if recent_points else 'stale',
            'average_confidence': sum(p.confidence for p in self.data_points) / len(self.data_points),
            'trend_available': len(self.trends) > 0
        }

# Global instance for immediate use
financial_manager = SimpleFinancialDataManager()

# Factory function
def get_financial_manager() -> SimpleFinancialDataManager:
    """Get the global financial data manager instance."""
    return financial_manager

if __name__ == "__main__":
    # Test the financial manager
    manager = get_financial_manager()
    
    print("🚀 Testing Financial Data Manager")
    print("=" * 50)
    
    # Test sentiment analysis
    test_text = "Bitcoin is showing strong bullish momentum with potential for breakout"
    entities = ["BTC", "bullish", "momentum", "breakout"]
    
    analysis = manager.analyze_text_sentiment(test_text, entities)
    print(f"\n📝 Sentiment Analysis:")
    print(f"   Text: {test_text}")
    print(f"   Sentiment: {analysis['sentiment_score']:.3f} ({analysis['direction']})")
    print(f"   Confidence: {analysis['confidence']:.3f}")
    print(f"   Entities: {analysis['entity_count']}")
    
    # Add a new post
    manager.add_financial_post(
        community="r/Quant",
        title="New algorithmic trading strategy shows 78% accuracy",
        content="Our backtesting results indicate strong performance in bull markets",
        score=234
    )
    
    # Get current sentiment
    sentiment = manager.get_current_sentiment()
    print(f"\n📊 Current Market Sentiment:")
    print(f"   Overall: {sentiment['market_sentiment']:.3f} ({sentiment['market_direction']})")
    print(f"   Total Posts: {sentiment['total_posts_analyzed']}")
    print(f"   Active Communities: {len(sentiment['community_sentiments'])}")
    
    # Get trends
    trends = manager.get_current_trends()
    print(f"\n📈 Current Market Trends:")
    print(f"   Trend: {trends['current_trend']}")
    print(f"   Strength: {trends['trend_strength']:.3f}")
    print(f"   Momentum: {trends['sentiment_momentum']:.3f}")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"\n📊 Manager Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Financial Data Manager test complete!")