"""
sentiment_analyzer.py
---------------------
Provides basic sentiment analysis for user feedback using TextBlob.
"""

from textblob import TextBlob


def analyze_sentiment(text: str):
    """Return (sentiment_label, polarity_score)."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        return "positive", polarity
    elif polarity < -0.2:
        return "negative", polarity
    else:
        return "neutral", polarity
