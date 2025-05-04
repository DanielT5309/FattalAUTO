import logging
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FattalSearchResultPageMobile:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    SHOW_PRICES_BUTTONS = (By.XPATH, "//button[normalize-space()='הצג מחירים']")
    BOOK_ROOM_BUTTONS = (By.XPATH, "//button[normalize-space()='להזמנת חדר']")
    ROOM_PRICE_LOADED = (By.XPATH, "//button[contains(@id, 'room-price-button')]")

    def take_screenshot(self, name="error_screenshot"):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_dir = os.path.join(os.getcwd(), "Screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        path = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(path)
        logging.error(f"Screenshot saved: {path}")

    def wait_for_rooms_to_load(self):
        try:
            logging.info("ממתין לטעינת כרטיסי חדרים (מובייל)...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.BOOK_ROOM_BUTTONS)
            )
            logging.info("כרטיסי חדרים נטענו.")
        except Exception as e:
            logging.error(f"כשל בטעינת כרטיסי חדרים במובייל: {e}")
            self.take_screenshot("wait_for_rooms_failed")
            raise

    def wait_for_show_prices_button(self, timeout=25):
        """
        Waits until the 'הצג מחירים' button is present and interactable, but does NOT click it.
        Useful if you want to take a screenshot right after the button appears.
        """
        try:
            logging.info("ממתין להופעת כפתור 'הצג מחירים'...")
            show_price_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'הצג מחירים')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_price_button)
            logging.info("כפתור 'הצג מחירים' נמצא ומוכן.")
            return show_price_button  # In case you want to pass it elsewhere
        except Exception as e:
            self.take_screenshot("wait_for_show_prices_fail")
            logging.error(f"❌ לא הצליח להמתין לכפתור 'הצג מחירים': {e}")
            raise
    def click_show_prices_button(self):
        logging.info("מחפש ולוחץ על כפתור 'הצג מחירים'...")

        try:
            # Wait for any button that contains this text
            show_price_button = WebDriverWait(self.driver, 25).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'הצג מחירים')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_price_button)
            time.sleep(0.5)
            show_price_button.click()
            logging.info("כפתור 'הצג מחירים' נלחץ בהצלחה.")

        except Exception as e:
            self.take_screenshot("show_prices_click_fail")
            logging.error(f"Failed to click 'הצג מחירים': {e}")
            raise

    def click_first_show_prices_button(self):
        logging.info("מחפש כפתורי 'הצג מחירים' במובייל...")

        for attempt in range(3):
            try:
                show_buttons = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_all_elements_located(self.SHOW_PRICES_BUTTONS)
                )

                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(self.SHOW_PRICES_BUTTONS)
                )

                logging.info(f"נמצאו {len(show_buttons)} כפתורי 'הצג מחירים'.")
                show_buttons[0].click()
                logging.info("נלחץ כפתור 'הצג מחירים' הראשון.")
                return
            except Exception as e:
                logging.warning(f"ניסיון {attempt + 1}: הכפתור עדיין לא מוכן. ממתין...")
                time.sleep(3)

        try:
            show_buttons = self.driver.find_elements(*self.SHOW_PRICES_BUTTONS)
            if show_buttons:
                self.driver.execute_script("arguments[0].click();", show_buttons[0])
                logging.info("כפתור 'הצג מחירים' נלחץ באמצעות JS.")
            else:
                raise Exception("כפתור 'הצג מחירים' לא נמצא.")
        except Exception as e:
            logging.error(f"שגיאה בלחיצה על 'הצג מחירים': {e}")
            self.take_screenshot("show_prices_button_fallback_error")
            raise

    def click_book_room_button(self):
        logging.info("מחפש ולוחץ על כפתור 'להזמנת חדר'...")

        try:
            book_buttons = WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(), 'להזמנת חדר')]"))
            )

            visible_button = next((b for b in book_buttons if b.is_displayed()), None)

            if visible_button:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", visible_button)
                time.sleep(0.4)
                self.driver.execute_script("arguments[0].click();", visible_button)
                logging.info("נלחץ כפתור 'להזמנת חדר' בהצלחה.")
            else:
                raise Exception("No visible 'להזמנת חדר' button found.")

        except Exception as e:
            logging.error(f"שגיאה בלחיצה על 'להזמנת חדר': {e}")
            self.take_screenshot("book_room_button_error")
            raise

    def wait_for_prices_to_load(self):
        logging.info("ממתין להופעת כפתורי מחירים...")

        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(self.ROOM_PRICE_LOADED)
            )
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.ROOM_PRICE_LOADED)
            )
            logging.info("מחירי חדרים נטענו בהצלחה.")
        except Exception as e:
            logging.error(f"לא נמצאו מחירים תוך זמן סביר: {e}")
            self.take_screenshot("wait_for_prices_timeout")
            raise

    def no_results_found(self) -> bool:
        try:
            banner = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(),'לא נמצאו מלונות')]"))
            )
            if banner.is_displayed():
                logging.warning("אין תוצאות חיפוש — לא נמצאו מלונות.")
                return True
            return False
        except:
            return False

    def click_show_prices_regional(self):
        """
        Regional flow: Tries to locate and click 'הצג מחירים' using JS once it's found.
        Scrolls only when element exists. No unnecessary scrolling.
        """
        try:
            logging.info("[REGIONAL] מחפש כפתור 'הצג מחירים'...")

            # Try to locate the element first
            WebDriverWait(self.driver, 90).until(
                lambda d: d.find_elements(By.XPATH, "//button[contains(text(),'הצג מחירים')]")
            )
            buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(),'הצג מחירים')]")

            if not buttons:
                raise TimeoutException("'הצג מחירים' not found on the page.")

            target_btn = buttons[0]

            # Scroll to button using JS
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_btn)
            time.sleep(0.5)

            # Try clicking it via JS
            self.driver.execute_script("arguments[0].click();", target_btn)
            logging.info("נלחץ כפתור 'הצג מחירים' בהצלחה.")

        except Exception as e:
            self.take_screenshot("click_show_prices_regional_fail")
            logging.error(f"[REGIONAL] Failed to click 'הצג מחירים': {e}")
            raise

    def click_book_room_regional(self):
        """
        Regional flow (with flights): Clicks the correct 'להזמנת חדר' button from price box layout,
        with fallback selector and error-resilient behavior.
        """
        try:
            logging.info("[REGIONAL] Trying to click 'להזמנת חדר' from regional price container...")

            # Primary selector
            buttons = self.driver.find_elements(By.XPATH, "//button[contains(@id, 'room-price-button-choose-room')]")

            # Fallback selector if primary yields nothing
            if not buttons:
                logging.warning("[REGIONAL] No buttons found with primary selector. Trying fallback...")
                buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'להזמנת חדר')]")

            if not buttons:
                raise Exception("[REGIONAL] No 'להזמנת חדר' buttons found — both selectors failed.")

            for idx, btn in enumerate(buttons):
                try:
                    logging.debug(f"[REGIONAL] Trying button index {idx}: {btn.get_attribute('outerHTML')[:100]}...")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(btn))
                    btn.click()
                    logging.info("[REGIONAL] Clicked 'להזמנת חדר' successfully.")
                    return
                except Exception as e:
                    logging.warning(f"[REGIONAL] Failed to click button #{idx}: {e}")
                    continue

            # If none succeeded
            raise Exception("[REGIONAL] Couldn't click any 'להזמנת חדר' button after loop.")

        except Exception as e:
            self.take_screenshot("click_book_room_regional_fail")
            logging.error(f"[REGIONAL] Failed to click regional 'להזמנת חדר': {e}")
            raise


