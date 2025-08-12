import requests
from bs4 import BeautifulSoup
import time
import random
import logging

class MyntraReviewScraper:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        ]
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_random_header(self):
        return {'User-Agent': random.choice(self.user_agents)}

    def scrape_reviews(self, url, max_reviews=20):
        reviews = []
        headers = self.get_random_header()

        try:
            time.sleep(random.uniform(2, 5))
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            review_elements = soup.find_all('div', class_='user-review-userReviewWrapper')

            for element in review_elements:
                if len(reviews) >= max_reviews: break
                review_text = element.find('div', class_='user-review-reviewText').get_text(strip=True) if element.find('div', class_='user-review-reviewText') else "N/A"
                # Myntra often doesn't show author names
                author = "Myntra Customer"
                rating_div = element.find('div', class_='user-review-ratings')
                rating = rating_div.div.get_text(strip=True) if rating_div else "N/A"
                reviews.append({'text': review_text, 'author': author, 'rating': rating})
            
            self.logger.info(f"Scraped {len(reviews)} reviews from Myntra.")
            return reviews
        except Exception as e:
            self.logger.error(f"Myntra scraping error: {e}")
            return []
