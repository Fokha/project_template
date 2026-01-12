# ═══════════════════════════════════════════════════════════════
# SENTIMENT ANALYSIS TEMPLATE
# NLP-based sentiment analysis for financial text
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Install: pip install transformers torch
# 3. Analyze news, social media, reports
#
# ═══════════════════════════════════════════════════════════════

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


class SentimentLabel(Enum):
    """Sentiment categories."""
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    text: str
    label: SentimentLabel
    score: float                   # -1 to 1
    confidence: float              # 0 to 1
    keywords: List[str] = None     # Detected sentiment keywords
    entities: List[str] = None     # Detected entities (symbols, companies)


@dataclass
class AggregateSentiment:
    """Aggregated sentiment from multiple sources."""
    overall_label: SentimentLabel
    overall_score: float
    confidence: float
    source_count: int
    bullish_count: int
    bearish_count: int
    neutral_count: int
    results: List[SentimentResult] = None


# ═══════════════════════════════════════════════════════════════
# RULE-BASED SENTIMENT (No ML Dependencies)
# ═══════════════════════════════════════════════════════════════


class RuleBasedSentiment:
    """
    Simple rule-based sentiment analysis.

    No ML dependencies - uses keyword matching.
    """

    def __init__(self):
        # Bullish keywords and weights
        self.bullish_words = {
            # Strong bullish
            'surge': 2.0, 'soar': 2.0, 'skyrocket': 2.0, 'breakout': 1.8,
            'rally': 1.5, 'boom': 1.5, 'bullish': 1.5, 'moonshot': 2.0,
            # Moderate bullish
            'rise': 1.0, 'gain': 1.0, 'up': 0.8, 'higher': 0.8,
            'positive': 0.8, 'growth': 1.0, 'strong': 0.8, 'buy': 1.2,
            'outperform': 1.2, 'upgrade': 1.5, 'beat': 1.0, 'exceed': 1.0,
            'optimistic': 1.2, 'confident': 1.0, 'recovery': 1.0,
        }

        # Bearish keywords and weights
        self.bearish_words = {
            # Strong bearish
            'crash': -2.0, 'plunge': -2.0, 'collapse': -2.0, 'tumble': -1.8,
            'bearish': -1.5, 'selloff': -1.5, 'panic': -1.8, 'crisis': -2.0,
            # Moderate bearish
            'fall': -1.0, 'drop': -1.0, 'down': -0.8, 'lower': -0.8,
            'decline': -1.0, 'weak': -0.8, 'sell': -1.2, 'loss': -1.0,
            'underperform': -1.2, 'downgrade': -1.5, 'miss': -1.0,
            'concern': -0.8, 'risk': -0.5, 'warning': -1.0, 'fear': -1.2,
        }

        # Negation words
        self.negations = {'not', 'no', 'never', 'neither', 'hardly', 'barely'}

        # Financial entities pattern
        self.entity_pattern = re.compile(
            r'\b([A-Z]{2,5}USD|[A-Z]{2,5}/[A-Z]{2,5}|\$[A-Z]{2,5}|'
            r'gold|silver|bitcoin|btc|eth|xrp)\b',
            re.IGNORECASE
        )

    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text."""
        text_lower = text.lower()
        words = text_lower.split()

        # Track scores
        bullish_score = 0.0
        bearish_score = 0.0
        keywords_found = []

        # Check each word with negation handling
        for i, word in enumerate(words):
            # Clean word
            word_clean = re.sub(r'[^\w]', '', word)

            # Check for negation in previous words
            negated = False
            for j in range(max(0, i - 3), i):
                if words[j] in self.negations:
                    negated = True
                    break

            # Check bullish words
            if word_clean in self.bullish_words:
                score = self.bullish_words[word_clean]
                if negated:
                    score = -score * 0.5  # Negation flips and reduces
                bullish_score += max(0, score)
                bearish_score += abs(min(0, score))
                keywords_found.append(word_clean)

            # Check bearish words
            if word_clean in self.bearish_words:
                score = self.bearish_words[word_clean]
                if negated:
                    score = -score * 0.5
                bearish_score += abs(min(0, score))
                bullish_score += max(0, -score)
                keywords_found.append(word_clean)

        # Find entities
        entities = self.entity_pattern.findall(text)

        # Calculate final score (-1 to 1)
        total = bullish_score + bearish_score
        if total > 0:
            score = (bullish_score - bearish_score) / total
        else:
            score = 0.0

        # Determine label
        label = self._score_to_label(score)

        # Confidence based on keyword count
        confidence = min(1.0, len(keywords_found) / 5)

        return SentimentResult(
            text=text[:200] + "..." if len(text) > 200 else text,
            label=label,
            score=score,
            confidence=confidence,
            keywords=keywords_found,
            entities=list(set(entities)),
        )

    def _score_to_label(self, score: float) -> SentimentLabel:
        """Convert score to label."""
        if score >= 0.6:
            return SentimentLabel.VERY_BULLISH
        elif score >= 0.2:
            return SentimentLabel.BULLISH
        elif score <= -0.6:
            return SentimentLabel.VERY_BEARISH
        elif score <= -0.2:
            return SentimentLabel.BEARISH
        else:
            return SentimentLabel.NEUTRAL

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze multiple texts."""
        return [self.analyze(text) for text in texts]


# ═══════════════════════════════════════════════════════════════
# TRANSFORMER-BASED SENTIMENT (Requires transformers)
# ═══════════════════════════════════════════════════════════════


class FinBERTSentiment:
    """
    FinBERT-based sentiment analysis.

    Uses ProsusAI/finbert model trained on financial text.
    Requires: pip install transformers torch
    """

    def __init__(self, model_name: str = "ProsusAI/finbert"):
        self.model_name = model_name
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """Load FinBERT model."""
        try:
            from transformers import pipeline
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
            )
            logger.info(f"Loaded model: {self.model_name}")
        except ImportError:
            logger.warning("transformers not installed. Using rule-based fallback.")
            self.pipeline = None
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.pipeline = None

    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment using FinBERT."""
        if self.pipeline is None:
            # Fallback to rule-based
            fallback = RuleBasedSentiment()
            return fallback.analyze(text)

        # Truncate to model max length
        text_truncated = text[:512]

        # Get prediction
        result = self.pipeline(text_truncated)[0]

        # Map FinBERT labels to our labels
        label_map = {
            'positive': SentimentLabel.BULLISH,
            'negative': SentimentLabel.BEARISH,
            'neutral': SentimentLabel.NEUTRAL,
        }

        label = label_map.get(result['label'].lower(), SentimentLabel.NEUTRAL)
        confidence = result['score']

        # Convert to score (-1 to 1)
        if label == SentimentLabel.BULLISH:
            score = confidence
        elif label == SentimentLabel.BEARISH:
            score = -confidence
        else:
            score = 0.0

        # Upgrade to very bullish/bearish if high confidence
        if confidence > 0.9:
            if label == SentimentLabel.BULLISH:
                label = SentimentLabel.VERY_BULLISH
            elif label == SentimentLabel.BEARISH:
                label = SentimentLabel.VERY_BEARISH

        return SentimentResult(
            text=text[:200] + "..." if len(text) > 200 else text,
            label=label,
            score=score,
            confidence=confidence,
        )

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze multiple texts."""
        return [self.analyze(text) for text in texts]


# ═══════════════════════════════════════════════════════════════
# SENTIMENT AGGREGATOR
# ═══════════════════════════════════════════════════════════════


class SentimentAggregator:
    """Aggregate sentiment from multiple sources."""

    def __init__(self, analyzer=None):
        self.analyzer = analyzer or RuleBasedSentiment()

    def aggregate(
        self,
        texts: List[str],
        weights: List[float] = None
    ) -> AggregateSentiment:
        """
        Aggregate sentiment from multiple texts.

        Args:
            texts: List of texts to analyze
            weights: Optional weights per text (e.g., by recency/importance)

        Returns:
            AggregateSentiment with overall sentiment
        """
        if not texts:
            return AggregateSentiment(
                overall_label=SentimentLabel.NEUTRAL,
                overall_score=0.0,
                confidence=0.0,
                source_count=0,
                bullish_count=0,
                bearish_count=0,
                neutral_count=0,
            )

        # Default equal weights
        if weights is None:
            weights = [1.0] * len(texts)

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Analyze all texts
        results = self.analyzer.analyze_batch(texts)

        # Count sentiment types
        bullish_count = sum(1 for r in results if r.label in [
            SentimentLabel.BULLISH, SentimentLabel.VERY_BULLISH
        ])
        bearish_count = sum(1 for r in results if r.label in [
            SentimentLabel.BEARISH, SentimentLabel.VERY_BEARISH
        ])
        neutral_count = sum(1 for r in results if r.label == SentimentLabel.NEUTRAL)

        # Weighted average score
        weighted_score = sum(r.score * w for r, w in zip(results, weights))

        # Average confidence
        avg_confidence = sum(r.confidence for r in results) / len(results)

        # Determine overall label
        if weighted_score >= 0.6:
            overall_label = SentimentLabel.VERY_BULLISH
        elif weighted_score >= 0.2:
            overall_label = SentimentLabel.BULLISH
        elif weighted_score <= -0.6:
            overall_label = SentimentLabel.VERY_BEARISH
        elif weighted_score <= -0.2:
            overall_label = SentimentLabel.BEARISH
        else:
            overall_label = SentimentLabel.NEUTRAL

        return AggregateSentiment(
            overall_label=overall_label,
            overall_score=weighted_score,
            confidence=avg_confidence,
            source_count=len(texts),
            bullish_count=bullish_count,
            bearish_count=bearish_count,
            neutral_count=neutral_count,
            results=results,
        )


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Sample financial texts
    texts = [
        "Gold prices surge to new highs as investors seek safe haven amid market uncertainty.",
        "Bitcoin crashes 15% as regulatory concerns mount, panic selling ensues.",
        "The Federal Reserve holds rates steady, markets react with cautious optimism.",
        "XAUUSD shows strong bullish momentum with technical breakout above resistance.",
        "Analysts downgrade US30 outlook citing recession fears and weak economic data.",
        "Crypto market recovers slightly after yesterday's selloff.",
    ]

    # Rule-based analysis
    print("=" * 60)
    print("RULE-BASED SENTIMENT ANALYSIS")
    print("=" * 60)

    analyzer = RuleBasedSentiment()
    for text in texts:
        result = analyzer.analyze(text)
        print(f"\nText: {text[:60]}...")
        print(f"  Label: {result.label.value}")
        print(f"  Score: {result.score:.2f}")
        print(f"  Keywords: {result.keywords}")
        print(f"  Entities: {result.entities}")

    # Aggregate sentiment
    print("\n" + "=" * 60)
    print("AGGREGATED SENTIMENT")
    print("=" * 60)

    aggregator = SentimentAggregator(analyzer)
    aggregate = aggregator.aggregate(texts)

    print(f"\nOverall: {aggregate.overall_label.value}")
    print(f"Score: {aggregate.overall_score:.2f}")
    print(f"Confidence: {aggregate.confidence:.2f}")
    print(f"Sources: {aggregate.source_count}")
    print(f"Bullish: {aggregate.bullish_count}, Bearish: {aggregate.bearish_count}, Neutral: {aggregate.neutral_count}")
