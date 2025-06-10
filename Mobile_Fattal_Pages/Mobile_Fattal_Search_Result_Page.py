import logging
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
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
            WebDriverWait(self.driver, 25).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'הצג מחירים')]"))
            )
            show_price_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'הצג מחירים')]")
            for button in show_price_buttons:
                if button.is_displayed() and button.is_enabled():
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        actions = ActionChains(self.driver)
                        actions.move_to_element(button).click().perform()
                        logging.info("כפתור 'הצג מחירים' נלחץ בהצלחה.")
                        return
                    except Exception as inner_e:
                        logging.warning(f"ניסיון לחיצה נכשל על כפתור: {inner_e}")
                        continue
            raise Exception("No clickable 'הצג מחירים' button was found.")
        except Exception as e:
            logging.error(f"Error clicking 'הצג מחירים': {e}")

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
        logging.info("📍 מחפש ולוחץ על כפתור 'להזמנת חדר'...")

        try:
            # Try clicking the button by its full ID first — most precise
            button_by_id = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "room-price-button-choose-room_ShClub 10_3"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_by_id)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", button_by_id)
            logging.info("✅ נלחץ כפתור 'להזמנת חדר' לפי מזהה ID.")

        except TimeoutException:
            logging.warning("⚠️ כפתור לפי ID לא נמצא, מנסה לפי טקסט...")

            try:
                button_by_text = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='להזמנת חדר']"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_by_text)
                time.sleep(0.3)
                self.driver.execute_script("arguments[0].click();", button_by_text)
                logging.info("✅ נלחץ כפתור 'להזמנת חדר' לפי טקסט.")

            except Exception as fallback_error:
                logging.error(f"❌ שגיאה בלחיצה על 'להזמנת חדר' לפי טקסט: {fallback_error}")
                self.take_screenshot("book_room_button_error_text")
                raise

        except Exception as e:
            logging.error(f"❌ שגיאה בלחיצה על 'להזמנת חדר' לפי ID: {e}")
            self.take_screenshot("book_room_button_error_id")
            raise


        except TimeoutException as te:
            logging.error("⏰ Timeout waiting for 'להזמנת חדר' button to become visible.")
            self.take_screenshot("book_room_button_timeout")
            raise

        except Exception as e:
            logging.error(f"❌ שגיאה בלחיצה על 'להזמנת חדר': {e}")
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

    def click_book_room_for_all_rooms(self, room_count=5):
        """
        Mobile flow: Click one 'הצג מחירים', then click 'הזמן' for each room in the unified flow.
        """
        try:
            logging.info(f"Attempting to book {room_count} rooms in mobile flow...")

            # Step 1: Click the single 'הצג מחירים'
            show_price_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'הצג מחירים')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_price_button)
            self.driver.execute_script("arguments[0].click();", show_price_button)
            logging.info("Clicked 'הצג מחירים' button (single expected in mobile).")

            # Step 2: Sequentially click 'הזמן' buttons for each room
            for i in range(room_count):
                logging.info(f"Waiting for room selection {i + 1} 'הזמן' button...")

                book_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'הזמן')]"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book_button)
                time.sleep(0.3)
                self.driver.execute_script("arguments[0].click();", book_button)
                logging.info(f"Clicked 'הזמן' for room {i + 1}")
                time.sleep(1.0)  # Wait between steps to allow modal to update

            logging.info("✅ All room selections completed successfully.")

        except Exception as e:
            self.take_screenshot("multi_room_booking_fail")
            logging.error(f"❌ Failed during mobile room booking flow: {e}")
            raise

    def click_show_then_book_room_with_fallback(self):
        logging.info("🔁 מנסה קודם ללחוץ על 'הצג מחירים', ואם לא קיים — מנסה 'להזמנת חדר' ישירות...")

        try:
            # Try clicking 'הצג מחירים' button
            self.click_show_prices_button()
            logging.info("✅ הצליח ללחוץ על כפתור 'הצג מחירים'. לוקח צילום מסך...")
            self.take_screenshot("room_selection")
        except Exception as e:
            logging.warning(f"⚠️ כפתור 'הצג מחירים' לא נמצא או לא לחיץ: {e}")
            logging.info("🡆 מנסה לעבור ישירות ללחיצה על כפתור 'להזמנת חדר'.")

        try:
            self.click_book_room_button()
            logging.info("✅ נלחץ כפתור 'להזמנת חדר'.")
        except Exception as e:
            logging.error(f"❌ נכשל בלחיצה על כפתור 'להזמנת חדר' לאחר ניסיון ב'מחירים': {e}")
            self.take_screenshot("book_room_fallback_fail")
            raise
