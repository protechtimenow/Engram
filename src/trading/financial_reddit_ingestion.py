"""
===============================================================================
[Financial Neural Capacity - Reddit Data Ingestion]

Advanced Reddit API integration for real-time financial community data ingestion.
Supports sentiment analysis, entity recognition, and trend detection from financial subreddits.
===============================================================================
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import re
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialCommunity(Enum):
    """Reddit financial communities with their influence weights."""
    QUANT = ("r/Quant", 0.85)  # High influence - quantitative analysis
    FINANCE = ("r/finance", 0.75)  # High influence - general finance
    SECURITY_ANALYSIS = ("r/SecurityAnalysis", 0.80)  # High influence - security analysis
    WALLSTREETBETS = ("r/wallstreetbets", 0.60)  # Medium influence - retail sentiment
    PERSONAL_FINANCE = ("r/personalfinance", 0.50)  # Medium influence - personal finance
    ECONOMICS = ("r/Economics", 0.70)  # High influence - economic analysis
    STOCKS = ("r/stocks", 0.65)  # Medium-high influence - stock discussion
    PORTFOLIOS = ("r/portfolios", 0.55)  # Medium influence - portfolio management
    INVESTING = ("r/investing", 0.70)  # High influence - investing strategies
    VALUE_INVESTING = ("r/ValueInvesting", 0.75)  # High influence - value investing
    FLUENT_IN_FINANCE = ("r/FluentInFinance", 0.65)  # Medium-high influence - financial literacy

@dataclass
class FinancialPost:
    """Represents a financial post from Reddit."""
    id: str
    title: str
    content: str
    author: str
    subreddit: str
    created_utc: float
    score: int
    num_comments: int
    sentiment_score: Optional[float] = None
    entities: Optional[List[str]] = None
    influence_weight: Optional[float] = None

@dataclass
class FinancialSentiment:
    """Represents financial sentiment analysis results."""
    community: str
    sentiment_score: float  # -1.0 (bearish) to +1.0 (bullish)
    confidence: float
    post_count: int
    timestamp: datetime
    trending_entities: List[str]

class RedditFinancialIngestion:
    """
    Advanced Reddit financial data ingestion with real-time processing
    and neural hash integration capabilities.
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.access_token = None
        self.token_expires = 0
        
        # Rate limiting
        self.rate_limit_remaining = 60
        self.rate_limit_reset = time.time() + 60
        
        # Community configurations
        self.communities = {community.value[0]: community for community in FinancialCommunity}
        
        # Data storage
        self.recent_posts: Dict[str, FinancialPost] = {}
        self.sentiment_history: Dict[str, List[FinancialSentiment]] = {}
        
        # Financial entity patterns
        self.stock_pattern = re.compile(r'\$([A-Z]{1,5})')
        self.crypto_pattern = re.compile(r'\b(BTC|ETH|USDT|USDC|BNB|XRP|ADA|SOL|DOGE|DOT|AVAX)\b')
        self.financial_terms = {
            'bullish', 'bearish', 'long', 'short', 'call', 'put', 'market', 'stock',
            'crypto', 'bitcoin', 'ethereum', 'trading', 'investment', 'portfolio',
            'dividend', 'yield', 'volatility', 'hedge', 'arbitrage', 'liquidity'
        }
        
        # Session for HTTP requests
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize the HTTP session and authenticate with Reddit."""
        self.session = aiohttp.ClientSession()
        await self._authenticate()
    
    async def _authenticate(self):
        """Authenticate with Reddit API using OAuth2."""
        if time.time() < self.token_expires and self.access_token:
            return
        
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        data = {
            'grant_type': 'client_credentials',
            'user_agent': self.user_agent
        }
        
        headers = {'User-Agent': self.user_agent}
        
        async with self.session.post(
            'https://www.reddit.com/api/v1/access_token',
            auth=auth,
            data=data,
            headers=headers
        ) as response:
            if response.status == 200:
                token_data = await response.json()
                self.access_token = token_data['access_token']
                self.token_expires = time.time() + token_data['expires_in'] - 60
                logger.info("✅ Successfully authenticated with Reddit API")
            else:
                raise Exception(f"Reddit authentication failed: {response.status}")
    
    async def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Make authenticated request to Reddit API with rate limiting."""
        await self._rate_limit_wait()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': self.user_agent
        }
        
        async with self.session.get(url, headers=headers, params=params) as response:
            # Update rate limit info
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 60))
            self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
            
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                logger.warning("⚠️ Rate limit hit, waiting...")
                await asyncio.sleep(5)
                return await self._make_request(url, params)
            else:
                raise Exception(f"Reddit API error: {response.status}")
    
    async def _rate_limit_wait(self):
        """Wait if rate limit is approaching."""
        if self.rate_limit_remaining < 5:
            wait_time = max(0, self.rate_limit_reset - time.time())
            if wait_time > 0:
                logger.info(f"⏳ Rate limit wait: {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
    
    async def fetch_community_posts(self, community: str, limit: int = 100) -> List[FinancialPost]:
        """
        Fetch recent posts from a financial community.
        
        Args:
            community: Reddit community name (e.g., 'r/Quant')
            limit: Number of posts to fetch
            
        Returns:
            List of FinancialPost objects
        """
        if community not in self.communities:
            raise ValueError(f"Unsupported community: {community}")
        
        url = f"https://oauth.reddit.com/{community}/hot"
        params = {'limit': limit, 't': 'day'}  # Last day's posts
        
        try:
            response_data = await self._make_request(url, params)
            posts = []
            
            for post_data in response_data['data']['children']:
                post_info = post_data['data']
                
                # Create FinancialPost object
                post = FinancialPost(
                    id=post_info['id'],
                    title=post_info['title'],
                    content=post_info.get('selftext', ''),
                    author=post_info['author'],
                    subreddit=post_info['subreddit'],
                    created_utc=post_info['created_utc'],
                    score=post_info['score'],
                    num_comments=post_info['num_comments'],
                    influence_weight=self.communities[community].value[1]
                )
                
                # Extract financial entities
                post.entities = self._extract_financial_entities(post.title + ' ' + post.content)
                
                # Calculate sentiment
                post.sentiment_score = self._calculate_sentiment(post.title + ' ' + post.content)
                
                posts.append(post)
                self.recent_posts[post.id] = post
            
            logger.info(f"📊 Fetched {len(posts)} posts from {community}")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Error fetching posts from {community}: {str(e)}")
            return []
    
    def _extract_financial_entities(self, text: str) -> List[str]:
        """Extract financial entities from text."""
        entities = set()
        
        # Stock tickers
        stocks = self.stock_pattern.findall(text.upper())
        entities.update([f"${stock}" for stock in stocks])
        
        # Crypto symbols
        cryptos = self.crypto_pattern.findall(text.upper())
        entities.update(cryptos)
        
        # Financial terms
        words = text.lower().split()
        for word in words:
            if word in self.financial_terms:
                entities.add(word)
        
        return list(entities)
    
    def _calculate_sentiment(self, text: str) -> float:
        """
        Calculate financial sentiment score.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score from -1.0 (bearish) to +1.0 (bullish)
        """
        # Simple sentiment analysis based on financial keywords
        bullish_words = {
            'buy', 'long', 'bullish', 'rally', 'surge', 'gain', 'profit', 'growth',
            'breakout', 'momentum', 'bull', 'call', 'up', 'rise', 'increase', 'strong'
        }
        
        bearish_words = {
            'sell', 'short', 'bearish', 'drop', 'fall', 'loss', 'decline', 'recession',
            'crash', 'downturn', 'bear', 'put', 'down', 'decrease', 'weak', 'fear'
        }
        
        words = text.lower().split()
        bullish_count = sum(1 for word in words if word in bullish_words)
        bearish_count = sum(1 for word in words if word in bearish_words)
        
        total_financial_words = bullish_count + bearish_count
        if total_financial_words == 0:
            return 0.0  # Neutral
        
        # Calculate sentiment score
        sentiment = (bullish_count - bearish_count) / total_financial_words
        return max(-1.0, min(1.0, sentiment))
    
    async def fetch_all_communities(self) -> Dict[str, List[FinancialPost]]:
        """Fetch posts from all configured financial communities."""
        all_posts = {}
        
        tasks = []
        for community in self.communities.keys():
            task = asyncio.create_task(self.fetch_community_posts(community, limit=50))
            tasks.append((community, task))
        
        # Wait for all tasks to complete
        for community, task in tasks:
            try:
                posts = await task
                all_posts[community] = posts
            except Exception as e:
                logger.error(f"❌ Error fetching {community}: {str(e)}")
                all_posts[community] = []
        
        return all_posts
    
    def calculate_community_sentiment(self, community: str) -> FinancialSentiment:
        """
        Calculate aggregated sentiment for a community.
        
        Args:
            community: Community name
            
        Returns:
            FinancialSentiment object
        """
        community_posts = [post for post in self.recent_posts.values() if post.subreddit == community]
        
        if not community_posts:
            return FinancialSentiment(
                community=community,
                sentiment_score=0.0,
                confidence=0.0,
                post_count=0,
                timestamp=datetime.now(),
                trending_entities=[]
            )
        
        # Weighted sentiment calculation
        total_weight = 0
        weighted_sentiment = 0
        all_entities = []
        
        for post in community_posts:
            weight = post.influence_weight * (1 + post.score / 1000)  # Score-based weighting
            weighted_sentiment += post.sentiment_score * weight
            total_weight += weight
            all_entities.extend(post.entities or [])
        
        avg_sentiment = weighted_sentiment / total_weight if total_weight > 0 else 0
        
        # Calculate confidence based on post count and engagement
        confidence = min(1.0, len(community_posts) / 50)  # More posts = higher confidence
        
        # Find trending entities
        entity_counts = {}
        for entity in all_entities:
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
        
        trending_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        trending_entities = [entity for entity, count in trending_entities]
        
        return FinancialSentiment(
            community=community,
            sentiment_score=avg_sentiment,
            confidence=confidence,
            post_count=len(community_posts),
            timestamp=datetime.now(),
            trending_entities=trending_entities
        )
    
    def get_market_overview(self) -> Dict:
        """Get comprehensive market sentiment overview."""
        community_sentiments = {}
        
        for community in self.communities.keys():
            sentiment = self.calculate_community_sentiment(community)
            community_sentiments[community] = sentiment
            self.sentiment_history.setdefault(community, []).append(sentiment)
        
        # Calculate overall market sentiment
        overall_sentiment = 0
        total_weight = 0
        
        for sentiment in community_sentiments.values():
            if sentiment.post_count > 0:
                weight = sentiment.confidence * sentiment.post_count
                overall_sentiment += sentiment.sentiment_score * weight
                total_weight += weight
        
        market_sentiment = overall_sentiment / total_weight if total_weight > 0 else 0
        
        return {
            'market_sentiment': market_sentiment,
            'market_direction': 'bullish' if market_sentiment > 0.1 else 'bearish' if market_sentiment < -0.1 else 'neutral',
            'community_sentiments': community_sentiments,
            'total_posts_analyzed': len(self.recent_posts),
            'timestamp': datetime.now().isoformat()
        }
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()

# Factory function for easy instantiation
def create_reddit_ingestion(client_id: str, client_secret: str, user_agent: str) -> RedditFinancialIngestion:
    """
    Create a configured Reddit financial ingestion instance.
    
    Args:
        client_id: Reddit API client ID
        client_secret: Reddit API client secret
        user_agent: User agent string
        
    Returns:
        Configured RedditFinancialIngestion instance
    """
    return RedditFinancialIngestion(client_id, client_secret, user_agent)

# Example usage
if __name__ == "__main__":
    async def main():
        # Configuration (replace with actual credentials)
        CLIENT_ID = "your_client_id"
        CLIENT_SECRET = "your_client_secret"
        USER_AGENT = "EngramFinancial/1.0"
        
        # Create ingestion instance
        ingestion = create_reddit_ingestion(CLIENT_ID, CLIENT_SECRET, USER_AGENT)
        
        try:
            await ingestion.initialize()
            
            # Fetch posts from all communities
            all_posts = await ingestion.fetch_all_communities()
            
            # Get market overview
            market_overview = ingestion.get_market_overview()
            
            print("📈 Market Overview:")
            print(f"Overall Sentiment: {market_overview['market_sentiment']:.3f}")
            print(f"Market Direction: {market_overview['market_direction']}")
            print(f"Total Posts Analyzed: {market_overview['total_posts_analyzed']}")
            
            print("\n📊 Community Sentiments:")
            for community, sentiment in market_overview['community_sentiments'].items():
                if sentiment.post_count > 0:
                    print(f"{community}: {sentiment.sentiment_score:.3f} ({sentiment.post_count} posts)")
            
        finally:
            await ingestion.close()
    
    asyncio.run(main())