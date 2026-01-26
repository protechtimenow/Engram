"""
===============================================================================
[Financial Neural Sentiment Analysis]

Advanced neural network pathways for financial sentiment analysis and pattern recognition.
Integrates with Engram's neural hashing system for context-aware financial processing.
===============================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import math

from neural_hashing import NeuralHashingModule, NeuralHashConfig
from financial_reddit_ingestion import FinancialPost, FinancialSentiment

@dataclass
class FinancialSentimentConfig:
    """Configuration for financial sentiment neural pathways."""
    # Model architecture
    vocab_size: int = 10000
    embedding_dim: int = 256
    hidden_dim: int = 512
    num_layers: int = 3
    num_heads: int = 8
    dropout: float = 0.1
    
    # Financial-specific parameters
    max_entities: int = 1000
    entity_embedding_dim: int = 128
    sentiment_scale: float = 1.0  # Scale factor for sentiment output
    
    # Neural hashing integration
    enable_hash_integration: bool = True
    hash_weight: float = 0.2
    
    # Device configuration
    device: str = "cuda" if torch.cuda.is_available() else "cpu"

class FinancialEntityEncoder(nn.Module):
    """Neural encoder for financial entities (stocks, crypto, indicators)."""
    
    def __init__(self, config: FinancialSentimentConfig):
        super().__init__()
        self.config = config
        
        # Entity embedding layers
        self.entity_embedding = nn.Embedding(config.max_entities, config.entity_embedding_dim)
        self.entity_type_embedding = nn.Embedding(4, config.entity_embedding_dim)  # stock, crypto, indicator, term
        
        # Entity processing layers
        self.entity_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=config.entity_embedding_dim,
                nhead=4,
                dropout=config.dropout,
                batch_first=True
            ),
            num_layers=2
        )
        
        # Output projection
        self.entity_projection = nn.Linear(config.entity_embedding_dim, config.hidden_dim)
    
    def forward(self, entity_ids: torch.Tensor, entity_types: torch.Tensor) -> torch.Tensor:
        """
        Encode financial entities.
        
        Args:
            entity_ids: [B, N] - Entity token IDs
            entity_types: [B, N] - Entity type IDs (0=stock, 1=crypto, 2=indicator, 3=term)
            
        Returns:
            torch.Tensor: [B, hidden_dim] - Encoded entity representations
        """
        # Get embeddings
        entity_embeds = self.entity_embedding(entity_ids)
        type_embeds = self.entity_type_embedding(entity_types)
        
        # Combine embeddings
        combined_embeds = entity_embeds + type_embeds
        
        # Process through transformer
        encoded_entities = self.entity_encoder(combined_embeds)
        
        # Global pooling
        pooled_entities = torch.mean(encoded_entities, dim=1)  # [B, entity_embedding_dim]
        
        # Project to hidden dimension
        output = self.entity_projection(pooled_entities)
        
        return output

class FinancialSentimentTransformer(nn.Module):
    """Advanced transformer for financial sentiment analysis."""
    
    def __init__(self, config: FinancialSentimentConfig):
        super().__init__()
        self.config = config
        
        # Token embedding and positional encoding
        self.token_embedding = nn.Embedding(config.vocab_size, config.embedding_dim)
        self.pos_encoding = PositionalEncoding(config.embedding_dim, dropout=config.dropout)
        
        # Main transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.embedding_dim,
            nhead=config.num_heads,
            dim_feedforward=config.hidden_dim,
            dropout=config.dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=config.num_layers)
        
        # Sentiment classification head
        self.sentiment_head = nn.Sequential(
            nn.Linear(config.embedding_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim // 2, 1)  # Single sentiment score
        )
        
        # Confidence estimation head
        self.confidence_head = nn.Sequential(
            nn.Linear(config.embedding_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim, 1),
            nn.Sigmoid()  # Confidence between 0 and 1
        )
    
    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass for sentiment analysis.
        
        Args:
            input_ids: [B, L] - Token IDs
            attention_mask: [B, L] - Attention mask
            
        Returns:
            Tuple[torch.Tensor, torch.Tensor]: (sentiment_scores, confidence_scores)
        """
        # Token embeddings
        token_embeds = self.token_embedding(input_ids)
        
        # Add positional encoding
        embedded = self.pos_encoding(token_embeds)
        
        # Apply attention mask if provided
        if attention_mask is not None:
            # Create key padding mask for transformer
            key_padding_mask = ~attention_mask.bool()
        else:
            key_padding_mask = None
        
        # Transformer processing
        transformer_output = self.transformer(embedded, src_key_padding_mask=key_padding_mask)
        
        # Global pooling (use mean of non-padded tokens)
        if attention_mask is not None:
            # Masked mean pooling
            mask_expanded = attention_mask.unsqueeze(-1).float()
            masked_output = transformer_output * mask_expanded
            pooled = torch.sum(masked_output, dim=1) / torch.sum(mask_expanded, dim=1)
        else:
            pooled = torch.mean(transformer_output, dim=1)
        
        # Sentiment and confidence prediction
        sentiment_logits = self.sentiment_head(pooled)
        sentiment_scores = torch.tanh(sentiment_logits) * self.config.sentiment_scale  # Scale to [-1, 1]
        
        confidence_scores = self.confidence_head(pooled)
        
        return sentiment_scores, confidence_scores

class PositionalEncoding(nn.Module):
    """Positional encoding for transformer inputs."""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)

class FinancialNeuralPathways:
    """
    Main class for financial neural pathways integration with Engram.
    Combines sentiment analysis, entity recognition, and neural hashing.
    """
    
    def __init__(self, config: FinancialSentimentConfig, neural_hasher: Optional[NeuralHashingModule] = None):
        self.config = config
        self.device = torch.device(config.device)
        
        # Initialize neural components
        self.sentiment_transformer = FinancialSentimentTransformer(config).to(self.device)
        self.entity_encoder = FinancialEntityEncoder(config).to(self.device)
        
        # Neural hashing integration
        self.neural_hasher = neural_hasher
        if config.enable_hash_integration and neural_hasher:
            self.hash_integration_layer = nn.Linear(
                config.embedding_dim + neural_hasher.config.max_context_length,
                config.embedding_dim
            ).to(self.device)
        
        # Financial vocabulary and entity mappings
        self.entity_to_id = {}
        self.entity_type_to_id = {
            'stock': 0,
            'crypto': 1,
            'indicator': 2,
            'term': 3
        }
        self.next_entity_id = 0
        
        # Model state
        self.training_history = []
        self.performance_metrics = {}
    
    def register_entity(self, entity: str, entity_type: str) -> int:
        """
        Register a new financial entity for encoding.
        
        Args:
            entity: Entity string (e.g., "AAPL", "$BTC")
            entity_type: Type of entity
            
        Returns:
            int: Entity ID
        """
        if entity not in self.entity_to_id:
            if self.next_entity_id >= self.config.max_entities:
                logger.warning("⚠️ Maximum entities reached, ignoring new entity")
                return -1
            
            self.entity_to_id[entity] = self.next_entity_id
            self.next_entity_id += 1
        
        return self.entity_to_id[entity]
    
    def encode_entities(self, entities: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encode a list of financial entities.
        
        Args:
            entities: List of entity strings
            
        Returns:
            Tuple[torch.Tensor, torch.Tensor]: (entity_ids, entity_types)
        """
        entity_ids = []
        entity_types = []
        
        for entity in entities:
            # Determine entity type
            if entity.startswith('$') and len(entity) <= 6:
                entity_type = 'stock'
            elif entity.upper() in ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE']:
                entity_type = 'crypto'
            elif entity in ['volatility', 'volume', 'rsi', 'macd', 'moving_average']:
                entity_type = 'indicator'
            else:
                entity_type = 'term'
            
            # Register and get ID
            entity_id = self.register_entity(entity, entity_type)
            if entity_id >= 0:
                entity_ids.append(entity_id)
                entity_types.append(self.entity_type_to_id[entity_type])
        
        # Convert to tensors
        entity_ids_tensor = torch.tensor(entity_ids, dtype=torch.long, device=self.device).unsqueeze(0)
        entity_types_tensor = torch.tensor(entity_types, dtype=torch.long, device=self.device).unsqueeze(0)
        
        return entity_ids_tensor, entity_types_tensor
    
    def analyze_sentiment(self, text: str, entities: List[str] = None) -> Dict[str, float]:
        """
        Analyze sentiment of financial text.
        
        Args:
            text: Text to analyze
            entities: List of financial entities in text
            
        Returns:
            Dict with sentiment analysis results
        """
        # Tokenize text (simple word tokenization for demo)
        tokens = text.lower().split()
        
        # Convert to token IDs (simple hash-based mapping)
        token_ids = []
        for token in tokens:
            token_id = hash(token) % self.config.vocab_size
            token_ids.append(token_id)
        
        # Prepare input tensors
        input_ids = torch.tensor([token_ids], dtype=torch.long, device=self.device)
        attention_mask = torch.ones_like(input_ids)
        
        # Encode entities if provided
        entity_encoding = None
        if entities and len(entities) > 0:
            entity_ids, entity_types = self.encode_entities(entities)
            entity_encoding = self.entity_encoder(entity_ids, entity_types)
        
        # Sentiment analysis
        with torch.no_grad():
            sentiment_scores, confidence_scores = self.sentiment_transformer(input_ids, attention_mask)
            
            # Extract results
            sentiment = sentiment_scores[0, 0].item()
            confidence = confidence_scores[0, 0].item()
            
            # Integrate with neural hashing if available
            hash_context = None
            if self.neural_hasher and self.config.enable_hash_integration:
                # Hash the text
                text_hashes = self.neural_hasher.hash_sequence(tokens)
                hash_tensor = torch.tensor([text_hashes], dtype=torch.long, device=self.device)
                
                # Get hash embeddings
                hash_embeddings = self.neural_hasher._hash_to_embedding(
                    hash_tensor[0], self.config.embedding_dim
                ).unsqueeze(0)
                
                # Combine with sentiment features
                combined_features = torch.cat([
                    self.sentiment_transformer.transformer(output)[-1:].mean(dim=1),
                    hash_embeddings
                ], dim=-1)
                
                hash_context = self.hash_integration_layer(combined_features)
        
        return {
            'sentiment_score': sentiment,
            'confidence': confidence,
            'direction': 'bullish' if sentiment > 0.1 else 'bearish' if sentiment < -0.1 else 'neutral',
            'entity_count': len(entities) if entities else 0,
            'hash_integration_active': hash_context is not None
        }
    
    def analyze_post_batch(self, posts: List[FinancialPost]) -> List[Dict[str, float]]:
        """
        Analyze sentiment for a batch of financial posts.
        
        Args:
            posts: List of FinancialPost objects
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        
        for post in posts:
            # Combine title and content
            full_text = f"{post.title} {post.content}"
            entities = post.entities or []
            
            # Analyze sentiment
            analysis = self.analyze_sentiment(full_text, entities)
            
            # Add post-specific information
            analysis.update({
                'post_id': post.id,
                'subreddit': post.subreddit,
                'score': post.score,
                'num_comments': post.num_comments
            })
            
            results.append(analysis)
        
        return results
    
    def detect_market_trends(self, sentiment_history: List[FinancialSentiment]) -> Dict:
        """
        Detect market trends from sentiment history.
        
        Args:
            sentiment_history: List of historical sentiment data
            
        Returns:
            Dict with trend analysis
        """
        if len(sentiment_history) < 3:
            return {'trend': 'insufficient_data', 'strength': 0.0}
        
        # Extract sentiment scores
        recent_scores = [s.sentiment_score for s in sentiment_history[-10:]]
        
        # Calculate trend direction
        if len(recent_scores) >= 3:
            # Simple linear regression for trend detection
            x = np.arange(len(recent_scores))
            y = np.array(recent_scores)
            
            # Calculate slope
            slope = np.polyfit(x, y, 1)[0]
            
            # Determine trend
            if slope > 0.05:
                trend = 'bullish_momentum'
            elif slope < -0.05:
                trend = 'bearish_momentum'
            elif np.mean(recent_scores) > 0.2:
                trend = 'bullish_consolidation'
            elif np.mean(recent_scores) < -0.2:
                trend = 'bearish_consolidation'
            else:
                trend = 'neutral'
            
            # Calculate trend strength
            strength = min(1.0, abs(slope) * 10)  # Scale slope to strength
            
            # Detect reversals
            if len(recent_scores) >= 5:
                recent_avg = np.mean(recent_scores[-3:])
                earlier_avg = np.mean(recent_scores[-5:-2])
                reversal_potential = abs(recent_avg - earlier_avg)
            else:
                reversal_potential = 0.0
            
            return {
                'trend': trend,
                'strength': strength,
                'slope': slope,
                'reversal_potential': reversal_potential,
                'current_sentiment': recent_scores[-1],
                'sentiment_momentum': recent_scores[-1] - recent_scores[-2] if len(recent_scores) >= 2 else 0.0
            }
        
        return {'trend': 'neutral', 'strength': 0.0}
    
    def get_performance_metrics(self) -> Dict:
        """Get model performance metrics."""
        return {
            'total_entities_registered': len(self.entity_to_id),
            'next_entity_id': self.next_entity_id,
            'max_entities': self.config.max_entities,
            'device': str(self.device),
            'hash_integration_enabled': self.config.enable_hash_integration,
            'neural_hasher_available': self.neural_hasher is not None
        }

# Factory function for easy instantiation
def create_financial_neural_pathways(
    vocab_size: int = 10000,
    embedding_dim: int = 256,
    hidden_dim: int = 512,
    enable_hash_integration: bool = True,
    neural_hasher: Optional[NeuralHashingModule] = None
) -> FinancialNeuralPathways:
    """
    Create a configured financial neural pathways instance.
    
    Args:
        vocab_size: Vocabulary size for token embedding
        embedding_dim: Embedding dimension
        hidden_dim: Hidden layer dimension
        enable_hash_integration: Whether to integrate with neural hashing
        neural_hasher: Neural hashing module for integration
        
    Returns:
        Configured FinancialNeuralPathways instance
    """
    config = FinancialSentimentConfig(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        enable_hash_integration=enable_hash_integration
    )
    
    return FinancialNeuralPathways(config, neural_hasher)

# Example usage
if __name__ == "__main__":
    # Create neural hasher for integration
    from neural_hashing import create_neural_hash_module
    neural_hasher = create_neural_hash_module()
    
    # Create financial neural pathways
    pathways = create_financial_neural_pathways(
        enable_hash_integration=True,
        neural_hasher=neural_hasher
    )
    
    # Test sentiment analysis
    test_text = "Bitcoin is showing strong bullish momentum with a breakout above $50,000. Market sentiment is very positive."
    test_entities = ["BTC", "$50,000", "bullish", "momentum"]
    
    analysis = pathways.analyze_sentiment(test_text, test_entities)
    
    print("🧠 Financial Neural Pathways Test:")
    print(f"Text: {test_text}")
    print(f"Sentiment: {analysis['sentiment_score']:.3f} ({analysis['direction']})")
    print(f"Confidence: {analysis['confidence']:.3f}")
    print(f"Entities: {analysis['entity_count']}")
    print(f"Hash Integration: {analysis['hash_integration_active']}")
    
    # Get performance metrics
    metrics = pathways.get_performance_metrics()
    print(f"\n📊 Performance Metrics: {metrics}")
    
    print("✅ Financial Neural Pathways Test Complete!")