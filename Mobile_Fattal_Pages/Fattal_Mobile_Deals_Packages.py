from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import random
import logging
from datetime import datetime
import os
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)


class FattalDealsPageMobile:
    def __init__(self, driver: webdriver.Chrome):
        self.wait = WebDriverWait(driver, 10)
        self.driver = driver

    def click_view_all_deals_link(self):
        """
        🔗 Clicks the 'לכל הדילים והחבילות' anchor link that navigates to the full deals page.
        """
        try:
            logging.info("🔗 Trying to click 'לכל הדילים והחבילות' link...")

            deals_link = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'לכל הדילים והחבילות')]"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", deals_link)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", deals_link)

            logging.info("✅ Clicked 'לכל הדילים והחבילות' link successfully.")

        except Exception as e:
            logging.error(f"❌ Failed to click 'לכל הדילים והחבילות': {e}")
            self.driver.save_screenshot("view_all_deals_click_fail.png")
            raise

    def click_view_more_deal_button(self):
        """
        📦 Clicks on the 'להזמנה ופרטים נוספים' button inside a specific deal card.
        Waits until the element is both visible and clickable to avoid race conditions.
        """
        try:
            logging.info("🔎 Waiting for 'להזמנה ופרטים נוספים' deal button to appear...")

            # Step 1: Wait for it to be visible
            visible_button = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "//a[contains(text(),'להזמנה ופרטים נוספים')]"
                ))
            )
            logging.info("👁️ Deal button is visible — waiting a moment for UI to stabilize...")

            # Step 2: Wait for it to be clickable (to avoid premature interaction)
            clickable_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//a[contains(text(),'להזמנה ופרטים נוספים')]"
                ))
            )

            # Scroll and click using JavaScript
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_button)
            time.sleep(0.4)
            self.driver.execute_script("arguments[0].click();", clickable_button)

            logging.info("✅ Clicked on 'להזמנה ופרטים נוספים' successfully.")

        except Exception as e:
            logging.error(f"❌ Failed to click 'להזמנה ופרטים נוספים': {e}")
            self.driver.save_screenshot("click_view_more_deal_error.png")
            raise

    def click_book_now_button(self):
        """
        🛎️ Clicks on the 'הזמן עכשיו' (Book Now) button after ensuring it's visible and clickable.
        Useful for the final booking confirmation.
        """
        try:
            logging.info("🛎️ Waiting for 'הזמן עכשיו' (Book Now) button to become visible...")

            button = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='הזמן עכשיו']"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='הזמן עכשיו']")))
            time.sleep(0.5)  # ⏳ UI animations or transitions

            self.driver.execute_script("arguments[0].click();", button)
            logging.info("✅ Clicked 'הזמן עכשיו' button successfully.")

        except Exception as e:
            logging.error(f"❌ Failed to click 'הזמן עכשיו' button: {e}")
            raise

    def click_continue_search_button_mobile(self):
        """
        📱 Clicks the 'המשך' (Continue) button on mobile search screen.
        Handles dynamic text like 'המשך - 2 לילות' by using partial match.
        """
        try:
            logging.info("📱 מנסה ללחוץ על כפתור 'המשך' הראשי במובייל...")

            button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[starts-with(text(), 'המשך')]"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[starts-with(text(), 'המשך')]")))
            time.sleep(0.3)  # Give animations time to settle

            self.driver.execute_script("arguments[0].click();", button)
            logging.info("✅ נלחץ כפתור 'המשך' (main search button במובייל)")

        except Exception as e:
            logging.warning("⚠️ לא נמצא כפתור לפי ID — מנסה לפי class...")
            try:
                alt_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "sc-f6382f5-0"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", alt_button)
                time.sleep(0.3)
                self.driver.execute_script("arguments[0].click();", alt_button)
                logging.info("✅ נלחץ כפתור 'המשך' לפי class")
            except Exception as e2:
                logging.error(f"❌ לא הצליח ללחוץ על כפתור 'המשך': {e2}")
                raise

    def click_continue_room_button(self):
        """
        ⏭️ Clicks the continue button on the room selection step.
        Ignores dynamic room/guest count in the text.
        """
        try:
            logging.info("🔍 Looking for 'המשך' button in room selection...")

            # Wait for element containing 'המשך' regardless of dynamic numbers
            continue_btn = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH, "//div[contains(text(), 'המשך')]"
                ))
            )

            # Scroll & click with JS (to avoid overlay issues)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
            time.sleep(0.4)
            self.driver.execute_script("arguments[0].click();", continue_btn)

            logging.info("✅ Clicked 'המשך' button in room selection.")
        except Exception as e:
            logging.error(f"❌ Failed to click 'המשך' in room selection: {e}")
            raise

    def click_mobile_search_button(self):
        """
        מנסה ללחוץ על כפתור 'המשך' במובייל לפי ID, ואם לא הצליח – לפי class fallback
        """
        try:
            logging.info("📱 מנסה ללחוץ על כפתור 'המשך' הראשי במובייל...")

            try:
                # ניסיון ראשון לפי ID
                search_btn = WebDriverWait(self.driver, 7).until(
                    EC.element_to_be_clickable((By.ID, "search-engine-search-button-mobile-buttonMain"))
                )
                logging.info("🔍 כפתור 'המשך' נמצא לפי ID")
            except TimeoutException:
                logging.warning("⚠️ לא נמצא כפתור לפי ID — מנסה לפי class...")
                search_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sc-f6382f5-0.edhILP"))
                )
                logging.info("🔍 כפתור 'המשך' נמצא לפי class")

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_btn)
            self.driver.execute_script("arguments[0].click();", search_btn)

            logging.info("✅ נלחץ כפתור 'המשך' (main search button במובייל)")

        except TimeoutException:
            logging.error("⏱️ Timeout – לא נמצא כפתור 'המשך' לפי ID וגם לפי class.")
            raise
        except Exception as e:
            logging.error(f"❌ שגיאה בלחיצה על כפתור 'המשך': {e}")
            raise

    def click_mobile_show_prices_button(self):
        """
        💸 לוחץ על כפתור 'הצג מחירים' בלי להתייחס למחיר שמוצג.
        מתמודד עם ID דינמי ומחכה לזמינות האלמנט.
        """
        try:
            logging.info("🔍 מחפש ולוחץ על כפתור 'הצג מחירים' במובייל...")

            # חפש לפי ID שמתחיל ב-room-price-button
            show_price_btn = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[starts-with(@id, 'room-price-button')]"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_price_btn)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", show_price_btn)

            logging.info("✅ נלחץ כפתור 'הצג מחירים' בהצלחה.")

        except Exception as e:
            logging.error(f"❌ שגיאה בלחיצה על כפתור 'הצג מחירים': {e}")
            raise
