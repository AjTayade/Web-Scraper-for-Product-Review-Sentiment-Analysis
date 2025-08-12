"""
Web scraper module for extracting product reviews from allowed domains.
Uses BeautifulSoup4 and requests for web scraping with ethical practices.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlparse, urljoin
import logging

class ReviewScraper:
    def __init__(self):
        # Allowed domains for ethical scraping
        self.allowed_domains = [
            'quotes.toscrape.com',  # Demo site for learning
            'books.toscrape.com',   # Demo site for learning
            'scrapethissite.com',   # Practice scraping site
            'httpbin.org',          # HTTP testing service
        ]

        # Headers to appear more like a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def is_valid_url(self, url):
        """Check if URL is from an allowed domain"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()

            # Remove www. if present
            if domain.startswith('www.'):
                domain = domain[4:]

            return domain in self.allowed_domains
        except Exception as e:
            self.logger.error(f"Error validating URL: {e}")
            return False

    def get_robots_txt(self, base_url):
        """Check robots.txt for scraping guidelines"""
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = requests.get(robots_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.logger.info(f"Found robots.txt at {robots_url}")
                return response.text
        except Exception as e:
            self.logger.warning(f"Could not fetch robots.txt: {e}")
        return None

    def scrape_reviews(self, url, max_reviews=100):
        """
        Scrape reviews from the given URL
        This is a demo implementation that works with allowed domains
        """
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]

            if domain == 'quotes.toscrape.com':
                return self._scrape_quotes_demo(url, max_reviews)
            elif domain == 'books.toscrape.com':
                return self._scrape_books_demo(url, max_reviews)
            elif domain == 'scrapethissite.com':
                return self._scrape_generic_demo(url, max_reviews)
            else:
                return self._generate_demo_reviews(max_reviews)

        except Exception as e:
            self.logger.error(f"Error scraping reviews: {e}")
            return []

    def _scrape_quotes_demo(self, url, max_reviews):
        """Scrape quotes from quotes.toscrape.com as demo reviews"""
        reviews = []
        try:
            # Add delay to be respectful
            time.sleep(random.uniform(1, 2))

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            quotes = soup.find_all('div', class_='quote')

            for quote in quotes[:max_reviews]:
                text_elem = quote.find('span', class_='text')
                author_elem = quote.find('small', class_='author')

                if text_elem and author_elem:
                    review_text = text_elem.get_text(strip=True)
                    author = author_elem.get_text(strip=True)

                    # Format as a product review
                    review = f"This product reminds me of what {author} said: {review_text}"
                    reviews.append({
                        'text': review,
                        'author': f"Reviewer_{len(reviews)+1}",
                        'rating': random.randint(3, 5)  # Demo ratings
                    })

            self.logger.info(f"Scraped {len(reviews)} quotes as demo reviews")

        except Exception as e:
            self.logger.error(f"Error scraping quotes: {e}")

        return reviews

    def _scrape_books_demo(self, url, max_reviews):
        """Scrape book titles from books.toscrape.com as demo reviews"""
        reviews = []
        try:
            time.sleep(random.uniform(1, 2))

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            books = soup.find_all('article', class_='product_pod')

            for book in books[:max_reviews]:
                title_elem = book.find('h3').find('a') if book.find('h3') else None
                price_elem = book.find('p', class_='price_color')

                if title_elem and price_elem:
                    title = title_elem.get('title', '').strip()
                    price = price_elem.get_text(strip=True)

                    # Generate demo review based on book info
                    sentiments = [
                        f"Great book '{title}' at {price}! Highly recommend.",
                        f"'{title}' was okay for {price}. Average quality.",
                        f"Disappointed with '{title}'. Not worth {price}.",
                        f"Amazing read! '{title}' exceeded expectations at {price}.",
                        f"'{title}' is a decent choice for {price}. Good value."
                    ]

                    review_text = random.choice(sentiments)
                    reviews.append({
                        'text': review_text,
                        'author': f"BookLover_{len(reviews)+1}",
                        'rating': random.randint(2, 5)
                    })

            self.logger.info(f"Scraped {len(reviews)} book-based demo reviews")

        except Exception as e:
            self.logger.error(f"Error scraping books: {e}")

        return reviews

    def _scrape_generic_demo(self, url, max_reviews):
        """Generic scraper for demo purposes"""
        try:
            time.sleep(random.uniform(1, 2))

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # Try to find any text content for demo purposes
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text_content = soup.get_text()
            lines = [line.strip() for line in text_content.splitlines() if line.strip()]

            reviews = []
            for i, line in enumerate(lines[:max_reviews]):
                if len(line) > 20:  # Only use substantial text
                    reviews.append({
                        'text': f"Review based on content: {line[:200]}...",
                        'author': f"User_{i+1}",
                        'rating': random.randint(2, 5)
                    })

            self.logger.info(f"Generated {len(reviews)} demo reviews from content")
            return reviews

        except Exception as e:
            self.logger.error(f"Error in generic scraping: {e}")
            return self._generate_demo_reviews(max_reviews)

    def _generate_demo_reviews(self, max_reviews):
        """Generate sample reviews for demonstration"""
        demo_reviews = [
            {"text": "This product is absolutely amazing! Great quality and fast shipping.", "author": "HappyCustomer123", "rating": 5},
            {"text": "Good value for money. Works as expected but nothing special.", "author": "PracticalBuyer", "rating": 3},
            {"text": "Poor quality, broke after one week. Would not recommend.", "author": "DisappointedUser", "rating": 1},
            {"text": "Excellent product! Exceeded my expectations completely.", "author": "SatisfiedShopper", "rating": 5},
            {"text": "Decent product but delivery was slow. Average experience overall.", "author": "RegularCustomer", "rating": 3},
            {"text": "Love this! Perfect for what I needed. Will buy again.", "author": "RepeatBuyer", "rating": 4},
            {"text": "Not worth the price. Found better alternatives elsewhere.", "author": "SmartShopper", "rating": 2},
            {"text": "Great customer service and product quality. Highly recommended!", "author": "ServiceExpert", "rating": 5},
            {"text": "It's okay. Does the job but could be better designed.", "author": "CriticalReviewer", "rating": 3},
            {"text": "Fantastic! This is exactly what I was looking for.", "author": "PerfectMatch", "rating": 5},
            {"text": "Mediocre quality for the price point. Expected more.", "author": "ValueSeeker", "rating": 2},
            {"text": "Outstanding product with excellent build quality!", "author": "QualityChecker", "rating": 5},
            {"text": "Could be better. Has some issues but generally works.", "author": "BalancedUser", "rating": 3},
            {"text": "Terrible experience. Product arrived damaged and unusable.", "author": "UnluckyBuyer", "rating": 1},
            {"text": "Great design and functionality. Very pleased with purchase.", "author": "DesignLover", "rating": 4}
        ]

        # Return random subset
        selected_reviews = random.sample(demo_reviews, min(max_reviews, len(demo_reviews)))
        self.logger.info(f"Generated {len(selected_reviews)} demo reviews")
        return selected_reviews
