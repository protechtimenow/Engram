"""
===============================================================================
[Financial Chain Reaction Testing - Unit & Component Tests]

Comprehensive unit and component tests for each hop in the financial data flow:
Reddit → Ingestion → Neural Pathways → Engram Memory → API → UI/Clients
===============================================================================
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import torch

# Import our modules
from financial_reddit_ingestion import (
    RedditFinancialIngestion, 
    FinancialPost, 
    FinancialSentiment,
    FinancialCommunity,
    create_reddit_ingestion
)
from financial_neural_pathways import (
    FinancialNeuralPathways,
    create_financial_neural_pathways
)
from neural_hashing import create_neural_hash_module

class TestFinancialIngestion:
    """Test Reddit financial data ingestion component."""
    
    @pytest.fixture
    def mock_reddit_response(self):
        """Mock Reddit API response structure."""
        return {
            'data': {
                'children': [
                    {
                        'data': {
                            'id': 'test123',
                            'title': 'Bitcoin is showing strong bullish momentum',
                            'selftext': 'Market analysis suggests continued upward trend',
                            'author': 'test_user',
                            'subreddit': 'r/Quant',
                            'created_utc': 1640995200.0,
                            'score': 245,
                            'num_comments': 89
                        }
                    },
                    {
                        'data': {
                            'id': 'test456',
                            'title': 'Tech stocks face headwinds from Fed policy',
                            'selftext': 'Analysis of recent market volatility',
                            'author': 'analyst_user',
                            'subreddit': 'r/finance',
                            'created_utc': 1640995300.0,
                            'score': 178,
                            'num_comments': 45
                        }
                    }
                ]
            }
        }
    
    @pytest.fixture
    def ingestion_instance(self):
        """Create Reddit ingestion instance for testing."""
        return create_reddit_ingestion(
            client_id="test_client",
            client_secret="test_secret",
            user_agent="TestEngram/1.0"
        )
    
    @pytest.mark.asyncio
    async def test_fetch_community_posts_structure(self, ingestion_instance, mock_reddit_response):
        """Test that fetching community posts maintains correct structure."""
        
        # Mock the HTTP request
        with patch.object(ingestion_instance, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_reddit_response
            
            await ingestion_instance.initialize()
            posts = await ingestion_instance.fetch_community_posts('r/Quant', limit=2)
            
            # Assert structure
            assert len(posts) == 2
            assert isinstance(posts[0], FinancialPost)
            assert posts[0].id == 'test123'
            assert posts[0].title == 'Bitcoin is showing strong bullish momentum'
            assert posts[0].subreddit == 'r/Quant'
            assert posts[0].score == 245
            assert posts[0].num_comments == 89
            
            # Assert entities were extracted
            assert len(posts[0].entities) > 0
            assert isinstance(posts[0].sentiment_score, float)
            assert -1.0 <= posts[0].sentiment_score <= 1.0
            
            # Assert influence weight was assigned
            assert posts[0].influence_weight == FinancialCommunity.QUANT.value[1]
    
    def test_financial_entity_extraction(self, ingestion_instance):
        """Test financial entity extraction patterns."""
        
        test_cases = [
            {
                'text': '$AAPL is surging while $TSLA drops',
                'expected_entities': ['$AAPL', '$TSLA']
            },
            {
                'text': 'Bitcoin and Ethereum are showing different patterns',
                'expected_entities': ['Bitcoin', 'Ethereum', 'BTC', 'ETH']
            },
            {
                'text': 'Market volatility and trading volume are key indicators',
                'expected_entities': ['volatility', 'trading']
            }
        ]
        
        for case in test_cases:
            entities = ingestion_instance._extract_financial_entities(case['text'])
            assert len(entities) > 0
            for expected in case['expected_entities']:
                assert any(expected in entity for entity in entities)
    
    def test_sentiment_calculation(self, ingestion_instance):
        """Test sentiment scoring accuracy."""
        
        test_cases = [
            {
                'text': 'bullish buy surge strong growth momentum',
                'expected_range': (0.5, 1.0)  # Strongly bullish
            },
            {
                'text': 'bearish sell drop decline crash',
                'expected_range': (-1.0, -0.5)  # Strongly bearish
            },
            {
                'text': 'market analysis report data',
                'expected_range': (-0.2, 0.2)  # Neutral
            }
        ]
        
        for case in test_cases:
            sentiment = ingestion_instance._calculate_sentiment(case['text'])
            min_val, max_val = case['expected_range']
            assert min_val <= sentiment <= max_val
    
    def test_community_sentiment_aggregation(self, ingestion_instance):
        """Test community sentiment calculation with weighting."""
        
        # Create mock posts with different scores
        posts = [
            FinancialPost(
                id='1', title='Bullish post', content='Great news', author='a',
                subreddit='r/Quant', created_utc=1640995200.0, score=100,
                num_comments=50, sentiment_score=0.8, entities=['BTC'],
                influence_weight=0.85
            ),
            FinancialPost(
                id='2', title='Bearish post', content='Bad news', author='b',
                subreddit='r/Quant', created_utc=1640995300.0, score=50,
                num_comments=25, sentiment_score=-0.6, entities=['AAPL'],
                influence_weight=0.85
            )
        ]
        
        # Add to ingestion instance
        for post in posts:
            ingestion_instance.recent_posts[post.id] = post
        
        # Calculate sentiment
        sentiment = ingestion_instance.calculate_community_sentiment('r/Quant')
        
        # Should be weighted average (biased toward bullish due to higher score)
        assert sentiment.sentiment_score > 0.0
        assert sentiment.post_count == 2
        assert sentiment.confidence > 0.0
        assert len(sentiment.trending_entities) > 0

class TestFinancialNeuralPathways:
    """Test financial neural pathways component."""
    
    @pytest.fixture
    def neural_pathways(self):
        """Create financial neural pathways for testing."""
        neural_hasher = create_neural_hash_module()
        return create_financial_neural_pathways(
            enable_hash_integration=True,
            neural_hasher=neural_hasher
        )
    
    def test_sentiment_analysis_structure(self, neural_pathways):
        """Test sentiment analysis returns correct structure."""
        
        analysis = neural_pathways.analyze_sentiment(
            "Bitcoin is showing strong bullish momentum",
            ["BTC", "bullish", "momentum"]
        )
        
        # Assert required fields
        required_fields = ['sentiment_score', 'confidence', 'direction', 'entity_count', 'hash_integration_active']
        for field in required_fields:
            assert field in analysis
        
        # Assert value ranges
        assert -1.0 <= analysis['sentiment_score'] <= 1.0
        assert 0.0 <= analysis['confidence'] <= 1.0
        assert analysis['direction'] in ['bullish', 'bearish', 'neutral']
        assert analysis['entity_count'] >= 0
        assert isinstance(analysis['hash_integration_active'], bool)
    
    def test_entity_registration(self, neural_pathways):
        """Test financial entity registration system."""
        
        entities = ["AAPL", "BTC", "volatility", "momentum"]
        
        for entity in entities:
            entity_id = neural_pathways.register_entity(entity, 'stock')
            assert entity_id >= 0
            assert entity in neural_pathways.entity_to_id
        
        # Test duplicate registration
        duplicate_id = neural_pathways.register_entity("AAPL", 'stock')
        original_id = neural_pathways.entity_to_id["AAPL"]
        assert duplicate_id == original_id
    
    def test_trend_detection_logic(self, neural_pathways):
        """Test trend detection with different patterns."""
        
        # Test bullish trend
        bullish_history = []
        for i in range(10):
            sentiment = FinancialSentiment(
                community='r/Quant',
                sentiment_score=0.1 + (i * 0.1),  # Increasing sentiment
                confidence=0.8,
                post_count=50,
                timestamp=datetime.now(),
                trending_entities=['BTC']
            )
            bullish_history.append(sentiment)
        
        trend_result = neural_pathways.detect_market_trends(bullish_history)
        
        assert trend_result['trend'] in ['bullish_momentum', 'bullish_consolidation']
        assert trend_result['strength'] > 0.0
        assert trend_result['slope'] > 0.0
        
        # Test bearish trend
        bearish_history = []
        for i in range(10):
            sentiment = FinancialSentiment(
                community='r/Quant',
                sentiment_score=0.1 - (i * 0.1),  # Decreasing sentiment
                confidence=0.8,
                post_count=50,
                timestamp=datetime.now(),
                trending_entities=['AAPL']
            )
            bearish_history.append(sentiment)
        
        bearish_trend = neural_pathways.detect_market_trends(bearish_history)
        
        assert bearish_trend['trend'] in ['bearish_momentum', 'bearish_consolidation']
        assert bearish_trend['strength'] > 0.0
        assert bearish_trend['slope'] < 0.0
    
    def test_insufficient_data_handling(self, neural_pathways):
        """Test trend detection with insufficient data."""
        
        # Test with 0, 1, 2 data points
        for i in range(3):
            history = [FinancialSentiment(
                community='r/Quant',
                sentiment_score=0.5,
                confidence=0.8,
                post_count=50,
                timestamp=datetime.now(),
                trending_entities=[]
            ) for _ in range(i)]
            
            result = neural_pathways.detect_market_trends(history)
            
            if i < 3:
                assert result['trend'] == 'insufficient_data'
                assert result['strength'] == 0.0

class TestNeuralHashIntegration:
    """Test neural hashing integration with financial data."""
    
    @pytest.fixture
    def neural_hasher(self):
        """Create neural hasher for testing."""
        return create_neural_hash_module()
    
    def test_financial_term_hashing(self, neural_hasher):
        """Test hashing of financial terms."""
        
        financial_terms = ["bullish", "bearish", "Bitcoin", "volatility"]
        hashes = neural_hasher.hash_sequence(financial_terms)
        
        assert len(hashes) == len(financial_terms)
        assert all(isinstance(h, int) for h in hashes)
        assert len(set(hashes)) >= len(hashes) * 0.8  # Low collision rate
    
    def test_context_memory_updates(self, neural_hasher):
        """Test context memory updates with financial data."""
        
        initial_stats = neural_hasher.get_hash_statistics()
        
        # Update with financial terms
        financial_terms = ["AAPL", "BTC", "momentum"]
        hashes = neural_hasher.hash_sequence(financial_terms)
        neural_hasher.update_context(financial_terms, hashes)
        
        updated_stats = neural_hasher.get_hash_statistics()
        
        assert updated_stats['total_hashes'] > initial_stats['total_hashes']
        assert updated_stats['memory_utilization'] > initial_stats['memory_utilization']
    
    def test_hash_integration_with_sentiment(self, neural_hasher):
        """Test that hash integration works with sentiment analysis."""
        
        neural_pathways = create_financial_neural_pathways(
            enable_hash_integration=True,
            neural_hasher=neural_hasher
        )
        
        analysis = neural_pathways.analyze_sentiment(
            "Bitcoin shows strong bullish momentum",
            ["BTC", "bullish"]
        )
        
        assert analysis['hash_integration_active'] == True

# Factory functions for test setup
def create_mock_financial_post(
    id: str = "test123",
    title: str = "Test post",
    subreddit: str = "r/Quant",
    sentiment_score: float = 0.5,
    score: int = 100
) -> FinancialPost:
    """Create a mock financial post for testing."""
    return FinancialPost(
        id=id,
        title=title,
        content=f"Content for {title}",
        author="test_user",
        subreddit=subreddit,
        created_utc=1640995200.0,
        score=score,
        num_comments=25,
        sentiment_score=sentiment_score,
        entities=["BTC", "momentum"],
        influence_weight=0.75
    )

def create_mock_sentiment_history(
    count: int = 10,
    trend: str = "bullish"
) -> list[FinancialSentiment]:
    """Create mock sentiment history for testing."""
    history = []
    base_time = datetime.now()
    
    for i in range(count):
        if trend == "bullish":
            sentiment_score = -0.5 + (i * 0.15)  # Increasing
        elif trend == "bearish":
            sentiment_score = 0.5 - (i * 0.15)   # Decreasing
        else:
            sentiment_score = 0.1 + (i * 0.01)    # Neutral/slight increase
        
        sentiment = FinancialSentiment(
            community='r/Quant',
            sentiment_score=sentiment_score,
            confidence=0.8,
            post_count=50,
            timestamp=base_time + timedelta(minutes=i),
            trending_entities=['BTC'] if i % 2 == 0 else ['AAPL']
        )
        history.append(sentiment)
    
    return history

if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running Financial Chain Reaction Unit Tests")
    
    # Test ingestion
    print("\n📱 Testing Reddit Ingestion...")
    ingestion = create_reddit_ingestion("test", "test", "test")
    
    # Test entity extraction
    entities = ingestion._extract_financial_entities("$AAPL and BTC are bullish")
    print(f"   Entity extraction: {entities}")
    assert len(entities) > 0
    
    # Test sentiment calculation
    sentiment = ingestion._calculate_sentiment("very bullish strong momentum buy")
    print(f"   Sentiment calculation: {sentiment}")
    assert sentiment > 0.0
    
    # Test neural pathways
    print("\n🧠 Testing Financial Neural Pathways...")
    neural_hasher = create_neural_hash_module()
    pathways = create_financial_neural_pathways(neural_hasher=neural_hasher)
    
    analysis = pathways.analyze_sentiment("Bitcoin is bullish", ["BTC"])
    print(f"   Sentiment analysis: {analysis}")
    assert 'sentiment_score' in analysis
    
    # Test trend detection
    history = create_mock_sentiment_history(10, "bullish")
    trends = pathways.detect_market_trends(history)
    print(f"   Trend detection: {trends['trend']} (strength: {trends['strength']})")
    assert trends['trend'] != 'insufficient_data'
    
    print("\n✅ Unit tests passed - Chain reaction components validated!")