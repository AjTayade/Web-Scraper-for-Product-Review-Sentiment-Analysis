from flask import Flask, render_template, request, flash
import os
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sentiment import SentimentAnalyzer

# Import all the new scraper classes
from amazon_scraper import AmazonReviewScraper
from flipkart_scraper import FlipkartReviewScraper
from jiomart_scraper import JioMartReviewScraper
from myntra_scraper import MyntraReviewScraper

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

analyzer = SentimentAnalyzer()
# Create a dictionary to hold an instance of each scraper
scrapers = {
    "amazon": AmazonReviewScraper(),
    "flipkart": FlipkartReviewScraper(),
    "jiomart": JioMartReviewScraper(),
    "myntra": MyntraReviewScraper()
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_reviews():
    try:
        product_url = request.form.get('product_url', '').strip()
        scraper_choice = request.form.get('scraper_choice')

        if not product_url or not scraper_choice:
            flash('Please select a retailer and enter a valid URL', 'error')
            return render_template('index.html')

        if scraper_choice not in scrapers:
            flash('Invalid retailer selected.', 'error')
            return render_template('index.html')

        scraper = scrapers[scraper_choice]
        flash(f'Using {scraper_choice.capitalize()} Scraper... Please wait.', 'info')
        reviews = scraper.scrape_reviews(product_url)
        
        if not reviews:
            flash('No reviews were found. The site may have blocked the request or the page structure has changed.', 'warning')
            return render_template('index.html')
        
        analyzed_reviews = analyzer.analyze_reviews(reviews)
        chart_data = analyzer.get_sentiment_counts(analyzed_reviews)
        chart_base64 = create_sentiment_chart(chart_data)
        grouped_reviews = analyzer.group_reviews_by_sentiment(analyzed_reviews)
        
        return render_template('results.html', 
                             reviews=analyzed_reviews[:10],
                             chart=chart_base64,
                             sentiment_counts=chart_data,
                             grouped_reviews=grouped_reviews,
                             total_reviews=len(analyzed_reviews))
        
    except Exception as e:
        app.logger.error(f"Error in analyze_reviews: {str(e)}")
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return render_template('index.html')

def create_sentiment_chart(sentiment_counts):
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        sentiments = list(sentiment_counts.keys())
        counts = list(sentiment_counts.values())
        colors = ['#2ecc71', '#e74c3c', '#95a5a6']
        bars = ax.bar(sentiments, counts, color=colors[:len(sentiments)])
        ax.set_title('Product Review Sentiment Distribution', fontsize=16, fontweight='bold')
        ax.set_xlabel('Sentiment', fontsize=12)
        ax.set_ylabel('Number of Reviews', fontsize=12)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        plt.tight_layout()
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return img_base64
    except Exception as e:
        app.logger.error(f"Error creating chart: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
