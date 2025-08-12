import requests
from bs4 import BeautifulSoup
import time
import random
import logging

class JioMartReviewScraper:
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

            review_elements = soup.find_all('div', class_='review-card')

            for element in review_elements:
                if len(reviews) >= max_reviews: break
                review_text = element.find('div', class_='review-text').p.get_text(strip=True) if element.find('div', class_='review-text') else "N/A"
                author = element.find('div', class_='reviewer-name').get_text(strip=True) if element.find('div', class_='reviewer-name') else "Anonymous"
                rating = element.find('span', class_='rating-star').get_text(strip=True) if element.find('span', class_='rating-star') else "N/A"
                reviews.append({'text': review_text, 'author': author, 'rating': rating})

            self.logger.info(f"Scraped {len(reviews)} reviews from JioMart.")
            return reviews
        except Exception as e:
            self.logger.error(f"JioMart scraping error: {e}")
            return []
