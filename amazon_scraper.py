import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from urllib.parse import urlparse

class AmazonReviewScraper:
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

            if "captcha" in response.text.lower():
                self.logger.error("Amazon CAPTCHA detected.")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            review_elements = soup.find_all('div', {'data-hook': 'review'})

            for element in review_elements:
                if len(reviews) >= max_reviews: break
                review_text = element.find('span', {'data-hook': 'review-body'}).get_text(strip=True) if element.find('span', {'data-hook': 'review-body'}) else "N/A"
                author = element.find('span', class_='a-profile-name').get_text(strip=True) if element.find('span', class_='a-profile-name') else "Anonymous"
                rating_element = element.find('i', {'data-hook': 'review-star-rating'})
                rating = "N/A"
                if rating_element and rating_element.find('span', class_='a-icon-alt'):
                    rating = rating_element.find('span', class_='a-icon-alt').get_text(strip=True).split(' ')[0]
                reviews.append({'text': review_text, 'author': author, 'rating': rating})

            self.logger.info(f"Scraped {len(reviews)} reviews from Amazon.")
            return reviews
        except Exception as e:
            self.logger.error(f"Amazon scraping error: {e}")
            return []
