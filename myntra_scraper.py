import time
import random
import logging
from bs4 import BeautifulSoup

# Selenium is used for browser automation to handle JavaScript-heavy sites
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class MyntraReviewScraper:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup Chrome options for Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run without opening a browser window
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

    def scrape_reviews(self, url, max_reviews=20):
        reviews = []
        # Initialize the Chrome driver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.chrome_options)
        
        try:
            self.logger.info(f"Navigating to Myntra URL: {url}")
            driver.get(url)
            
            # Wait for the page to load; adjust sleep time if necessary
            time.sleep(random.uniform(3, 6))

            # Myntra's reviews are inside a specific section. We need to find it.
            # The class names can change, this is the most fragile part.
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            review_elements = soup.find_all('div', class_='user-review-userReviewWrapper')

            if not review_elements:
                self.logger.warning("No review elements found. The page structure may have changed or reviews are not present.")
                return []

            for element in review_elements:
                if len(reviews) >= max_reviews:
                    break
                
                review_text_element = element.find('div', class_='user-review-reviewText')
                review_text = review_text_element.get_text(strip=True) if review_text_element else "N/A"
                
                # Myntra does not typically show author names, so we'll use a placeholder
                author = "Myntra Customer"

                rating_div = element.find('div', class_='user-review-ratings')
                rating = rating_div.div.get_text(strip=True) if rating_div else "N/A"

                if review_text != "N/A":
                    reviews.append({'text': review_text, 'author': author, 'rating': rating})

            self.logger.info(f"Successfully scraped {len(reviews)} reviews from Myntra.")
            return reviews
            
        except Exception as e:
            self.logger.error(f"An error occurred during Myntra scraping with Selenium: {e}")
            return []
        finally:
            # Always close the browser
            driver.quit()
