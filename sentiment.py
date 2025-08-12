"""
Sentiment analysis module using TextBlob for product review analysis.
Processes reviews and categorizes them into Positive, Negative, and Neutral sentiments.
"""

from textblob import TextBlob
import logging
from collections import defaultdict

class SentimentAnalyzer:
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Sentiment thresholds
        self.positive_threshold = 0.1
        self.negative_threshold = -0.1

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of a single text using TextBlob
        Returns: dict with polarity, subjectivity, and sentiment label
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Determine sentiment label
            if polarity > self.positive_threshold:
                sentiment = 'Positive'
            elif polarity < self.negative_threshold:
                sentiment = 'Negative'
            else:
                sentiment = 'Neutral'

            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'sentiment': sentiment
            }

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'sentiment': 'Neutral'
            }

    def analyze_reviews(self, reviews):
        """
        Analyze sentiment for a list of reviews
        Returns: list of reviews with added sentiment analysis
        """
        analyzed_reviews = []

        for review in reviews:
            try:
                # Get original review data
                review_text = review.get('text', '')
                author = review.get('author', 'Anonymous')
                rating = review.get('rating', 3)

                # Perform sentiment analysis
                sentiment_data = self.analyze_sentiment(review_text)

                # Combine original review with sentiment analysis
                analyzed_review = {
                    'text': review_text,
                    'author': author,
                    'rating': rating,
                    'polarity': sentiment_data['polarity'],
                    'subjectivity': sentiment_data['subjectivity'],
                    'sentiment': sentiment_data['sentiment']
                }

                analyzed_reviews.append(analyzed_review)

            except Exception as e:
                self.logger.error(f"Error processing review: {e}")
                continue

        self.logger.info(f"Analyzed {len(analyzed_reviews)} reviews")
        return analyzed_reviews

    def get_sentiment_counts(self, analyzed_reviews):
        """
        Count reviews by sentiment category
        Returns: dict with sentiment counts
        """
        sentiment_counts = defaultdict(int)

        for review in analyzed_reviews:
            sentiment = review.get('sentiment', 'Neutral')
            sentiment_counts[sentiment] += 1

        # Ensure all three categories are present
        for sentiment in ['Positive', 'Negative', 'Neutral']:
            if sentiment not in sentiment_counts:
                sentiment_counts[sentiment] = 0

        return dict(sentiment_counts)

    def group_reviews_by_sentiment(self, analyzed_reviews, max_per_group=5):
        """
        Group reviews by sentiment for display
        Returns: dict with sentiment categories as keys
        """
        grouped = {
            'Positive': [],
            'Negative': [],
            'Neutral': []
        }

        for review in analyzed_reviews:
            sentiment = review.get('sentiment', 'Neutral')
            if len(grouped[sentiment]) < max_per_group:
                grouped[sentiment].append(review)

        return grouped

    def get_sentiment_statistics(self, analyzed_reviews):
        """
        Calculate detailed sentiment statistics
        Returns: dict with comprehensive statistics
        """
        if not analyzed_reviews:
            return {
                'total_reviews': 0,
                'avg_polarity': 0.0,
                'avg_subjectivity': 0.0,
                'sentiment_distribution': {'Positive': 0, 'Negative': 0, 'Neutral': 0},
                'sentiment_percentages': {'Positive': 0.0, 'Negative': 0.0, 'Neutral': 0.0}
            }

        total_reviews = len(analyzed_reviews)
        total_polarity = sum(review['polarity'] for review in analyzed_reviews)
        total_subjectivity = sum(review['subjectivity'] for review in analyzed_reviews)

        avg_polarity = total_polarity / total_reviews
        avg_subjectivity = total_subjectivity / total_reviews

        # Get sentiment distribution
        sentiment_counts = self.get_sentiment_counts(analyzed_reviews)

        # Calculate percentages
        sentiment_percentages = {}
        for sentiment, count in sentiment_counts.items():
            sentiment_percentages[sentiment] = round((count / total_reviews) * 100, 1)

        return {
            'total_reviews': total_reviews,
            'avg_polarity': round(avg_polarity, 3),
            'avg_subjectivity': round(avg_subjectivity, 3),
            'sentiment_distribution': sentiment_counts,
            'sentiment_percentages': sentiment_percentages
        }

    def get_top_positive_negative(self, analyzed_reviews, top_n=3):
        """
        Get top positive and negative reviews based on polarity score
        Returns: dict with top positive and negative reviews
        """
        # Sort by polarity
        sorted_reviews = sorted(analyzed_reviews, key=lambda x: x['polarity'])

        # Get top negative (lowest polarity)
        top_negative = sorted_reviews[:top_n]

        # Get top positive (highest polarity)
        top_positive = sorted_reviews[-top_n:][::-1]  # Reverse to get highest first

        return {
            'top_positive': top_positive,
            'top_negative': top_negative
        }

    def export_results_csv(self, analyzed_reviews, filename='sentiment_results.csv'):
        """
        Export analyzed reviews to CSV format
        Returns: CSV content as string
        """
        try:
            import csv
            import io

            output = io.StringIO()
            fieldnames = ['text', 'author', 'rating', 'sentiment', 'polarity', 'subjectivity']
            writer = csv.DictWriter(output, fieldnames=fieldnames)

            writer.writeheader()
            for review in analyzed_reviews:
                writer.writerow({
                    'text': review['text'][:200] + '...' if len(review['text']) > 200 else review['text'],
                    'author': review['author'],
                    'rating': review['rating'],
                    'sentiment': review['sentiment'],
                    'polarity': review['polarity'],
                    'subjectivity': review['subjectivity']
                })

            csv_content = output.getvalue()
            output.close()

            self.logger.info(f"Exported {len(analyzed_reviews)} reviews to CSV")
            return csv_content

        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return None
