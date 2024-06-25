import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class AppleStoreScraper:
    def __init__(
        self, app_id="id389801252", chrome_driver_path="chromedriver", timeout=5
    ):
        self.app_id = app_id
        self.url = f"https://apps.apple.com/pl/app/instagram/{app_id}?l=pl"
        self.timeout = timeout

        self.service = Service(chrome_driver_path)
        self.options = Options()
        # self.options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.wait = WebDriverWait(self.driver, self.timeout)

        self.app_details = self.scrape()

    def get_element_text(self, by, value):
        try:
            return self.wait.until(EC.presence_of_element_located((by, value))).text
        except TimeoutException:
            logging.error(f"Timeout while waiting for element {value}")
            return None

    def get_visible_element_text(self, by, value):
        try:
            return self.wait.until(EC.visibility_of_element_located((by, value))).text
        except TimeoutException:
            logging.error(f"Timeout while waiting for visible element {value}")
            return None

    def get_element_attribute(self, by, value, attribute):
        try:
            return self.wait.until(
                EC.presence_of_element_located((by, value))
            ).get_attribute(attribute)
        except TimeoutException:
            logging.error(f"Timeout while waiting for element {value}")
            return None

    def click_element(self, by, value):
        try:
            element = self.wait.until(EC.element_to_be_clickable((by, value)))
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            element.click()
        except (TimeoutException, ElementClickInterceptedException) as e:
            logging.error(f"Error clicking element {value}: {e}")

    def scrape_app_details(self):
        self.driver.get(self.url)

        self.click_element(By.XPATH, "//button[@data-more-button]")

        titleAndContentRating = self.get_element_text(
            By.XPATH, '//h1[@class="product-header__title app-header__title"]'
        )

        image = (
            self.get_element_attribute(
                By.XPATH,
                '//picture[@class="we-artwork we-artwork--downloaded product-hero__artwork we-artwork--fullwidth we-artwork--ios-app-icon"]//source[@type="image/webp"]',
                "srcset",
            )
            .split(",")[0]
            .strip()
            .split(" ")[0]
        )

        developer = self.get_element_text(
            By.XPATH, '//h2[@class="product-header__identity app-header__identity"]/a'
        )

        app_rating = self.get_element_text(
            By.XPATH, '//figcaption[@class="we-rating-count star-rating__count"]'
        )

        size = self.get_element_text(
            By.XPATH,
            '//div[@class="information-list__item l-column small-12 medium-6 large-4 small-valign-top"]//dd[@class="information-list__item__definition"]',
        )

        category = self.get_element_text(
            By.XPATH,
            '//div[@class="information-list__item l-column small-12 medium-6 large-4 small-valign-top"]//dd[@class="information-list__item__definition"]/a',
        )

        title = titleAndContentRating.split(" ")[0]
        content_rating = titleAndContentRating.split(" ")[1]
        star_rating = app_rating.split("•")[0].strip()
        reviews_count = app_rating.split(":")[1]

        self.click_element(By.XPATH, '//button[@id="modal-trigger-ember11"]')

        updated_on = self.get_element_text(
            By.CSS_SELECTOR, ".version-history__item__release-date"
        )

        self.click_element(By.XPATH, '//button[@class="we-modal__close"]')

        details = {
            "title": title,
            "image": image,
            "size": size,
            "category": category,
            "contentRating": content_rating,
            "starRating": star_rating,
            "developer": developer,
            "reviewsCount": reviews_count,
            "updatedOn": updated_on,
        }

        return details

    def scrape(self):
        try:
            app_details = self.scrape_app_details()
            return app_details
        finally:
            self.driver.quit()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    scraper = AppleStoreScraper(
        chrome_driver_path="./chromedriver",
    )
    print(json.dumps(scraper.app_details, indent=2, ensure_ascii=False))
