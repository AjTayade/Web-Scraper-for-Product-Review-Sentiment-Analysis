"""
Flask Web Scraper for Product Review Sentiment Analysis
A deployable Python Flask web app that scrapes product reviews from allowed sites,
performs sentiment analysis using TextBlob, and visualizes results with Matplotlib.
"""

from flask import Flask, render_template, request, flash, jsonify
import os
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from scraper import ReviewScraper
from sentiment import SentimentAnalyzer

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize components
scraper = ReviewScraper()
analyzer = SentimentAnalyzer()

@app.route('/')
def index():
    """Render the main input form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_reviews():
    """Process the product URL and perform sentiment analysis"""
    try:
        product_url = request.form.get('product_url', '').strip()

        if not product_url:
            flash('Please enter a valid product URL', 'error')
            return render_template('index.html')

        # Validate URL format and allowed domains
        if not scraper.is_valid_url(product_url):
            flash('Please enter a valid URL from an allowed domain', 'error')
            return render_template('index.html')

        # Scrape reviews
        flash('Scraping reviews... Please wait.', 'info')
        reviews = scraper.scrape_reviews(product_url)

        if not reviews:
            flash('No reviews found or unable to scrape the page. Please try a different URL.', 'warning')
            return render_template('index.html')

        # Perform sentiment analysis
        analyzed_reviews = analyzer.analyze_reviews(reviews)

        # Generate visualization
        chart_data = analyzer.get_sentiment_counts(analyzed_reviews)
        chart_base64 = create_sentiment_chart(chart_data)

        # Group sample reviews by sentiment
        grouped_reviews = analyzer.group_reviews_by_sentiment(analyzed_reviews)

        return render_template('results.html', 
                             reviews=analyzed_reviews[:10],  # Show first 10 for display
                             chart=chart_base64,
                             sentiment_counts=chart_data,
                             grouped_reviews=grouped_reviews,
                             total_reviews=len(analyzed_reviews))

    except Exception as e:
        app.logger.error(f"Error in analyze_reviews: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('index.html')

def create_sentiment_chart(sentiment_counts):
    """Create a bar chart of sentiment distribution"""
    try:
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))

        sentiments = list(sentiment_counts.keys())
        counts = list(sentiment_counts.values())
        colors = ['#2ecc71', '#e74c3c', '#95a5a6']  # Green, Red, Gray

        bars = ax.bar(sentiments, counts, color=colors[:len(sentiments)])

        # Customize the chart
        ax.set_title('Product Review Sentiment Distribution', fontsize=16, fontweight='bold')
        ax.set_xlabel('Sentiment', fontsize=12)
        ax.set_ylabel('Number of Reviews', fontsize=12)

        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{count}', ha='center', va='bottom', fontweight='bold')

        # Style improvements
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, max(counts) * 1.1 if counts else 1)

        plt.tight_layout()

        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)

        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig)  # Important: close figure to free memory

        return img_base64

    except Exception as e:
        app.logger.error(f"Error creating chart: {str(e)}")
        return None

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal error: {str(error)}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html'), 500

if __name__ == '__main__':
    # For development
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
