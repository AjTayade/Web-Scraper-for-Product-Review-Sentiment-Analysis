import time
import random
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class SmartScraper:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # --- Stealth Options to Avoid Detection ---
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in the background
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

    def get_reviews(self, url, max_reviews=20):
        # --- Scraper Logic for All Sites ---
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        reviews = []
        try:
            self.logger.info(f"Navigating to {url} with smart scraper.")
            driver.get(url)

            # --- Intelligent Waits for Dynamic Content ---
            # This waits up to 15 seconds for the review section to appear.
            # We define different potential locators for each site.
            locators = {
                'amazon': (By.CSS_SELECTOR, "div[data-hook='review']"),
                'flipkart': (By.CSS_SELECTOR, "div._27M-vq"),
                'myntra': (By.CSS_SELECTOR, "div.user-review-userReviewWrapper"),
                'jiomart': (By.CSS_SELECTOR, "div.review-card")
            }
            
            domain = next((d for d in locators if d in url), None)
            if not domain:
                self.logger.error("URL does not match any supported retailer.")
                return []

            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located(locators[domain]))
            
            # Scroll to ensure all content is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
            time.sleep(random.uniform(2, 4)) # Allow time for scroll-triggered content

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # --- Call the correct parsing function based on domain ---
            if domain == 'amazon':
                reviews = self._parse_amazon(soup, max_reviews)
            elif domain == 'flipkart':
                reviews = self._parse_flipkart(soup, max_reviews)
            elif domain == 'myntra':
                reviews = self._parse_myntra(soup, max_reviews)
            elif domain == 'jiomart':
                reviews = self._parse_jiomart(soup, max_reviews)
            
            self.logger.info(f"Successfully scraped {len(reviews)} reviews.")
            return reviews
            
        except Exception as e:
            self.logger.error(f"A critical error occurred: {e}")
            return []
        finally:
            driver.quit()

    def _parse_amazon(self, soup, max_reviews):
        reviews = []
        for element in soup.find_all('div', {'data-hook': 'review'})[:max_reviews]:
            reviews.append({
                'text': element.find('span', {'data-hook': 'review-body'}).get_text(strip=True),
                'author': element.find('span', class_='a-profile-name').get_text(strip=True),
                'rating': element.find('i', {'data-hook': 'review-star-rating'}).get_text(strip=True).split(' ')[0]
            })
        return reviews

    def _parse_flipkart(self, soup, max_reviews):
        reviews = []
        for element in soup.find_all('div', class_='_27M-vq')[:max_reviews]:
            reviews.append({
                'text': element.find('div', class_='t-ZTKy').get_text(strip=True),
                'author': element.find('p', class_='_2sc7ZR').get_text(strip=True),
                'rating': element.find('div', class_='_3LWZlK').get_text(strip=True)
            })
        return reviews

    def _parse_myntra(self, soup, max_reviews):
        reviews = []
        for element in soup.find_all('div', class_='user-review-userReviewWrapper')[:max_reviews]:
            reviews.append({
                'text': element.find('div', class_='user-review-reviewText').get_text(strip=True),
                'author': 'Myntra Customer',
                'rating': element.find('div', class_='user-review-ratings').div.get_text(strip=True)
            })
        return reviews

    def _parse_jiomart(self, soup, max_reviews):
        reviews = []
        for element in soup.find_all('div', class_='review-card')[:max_reviews]:
            reviews.append({
                'text': element.find('div', class_='review-text').p.get_text(strip=True),
                'author': element.find('div', class_='reviewer-name').get_text(strip=True),
                'rating': element.find('span', class_='rating-star').get_text(strip=True)
            })
        return reviews
