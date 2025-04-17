import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class FattalSearchResultPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)


    SHOW_PRICES_BUTTONS = (By.XPATH, "//button[normalize-space()='הצג מחירים']")
    ROOM_CARD = (By.CSS_SELECTOR, "div.sc-2a344c4a-0.cQdWLm")
    BOOK_BUTTON_IN_CARD = (By.XPATH, ".//button[normalize-space()='להזמנת חדר']")
    ROOM_CARDS_WRAPPER = (By.CSS_SELECTOR, "div.sc-3f982010-0.OrVdk")  # or the real room wrapper
    ROOM_CARDS_LOADED = (By.XPATH, "//button[contains(text(), 'להזמנת חדר')]")


    def wait_for_rooms_to_load(self):
        try:
            logging.info("🛏️ Waiting for room cards to fully load...")

            # Option 1: Wait for the skeleton placeholders to disappear (if class changes)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located(self.ROOM_CARDS_LOADED)
            )

            logging.info("✅ Room cards are loaded.")
        except Exception as e:
            logging.error(f"❌ Room cards did not load in time: {e}")
            raise

    def click_first_show_prices(self):
        logging.info("🔎 Looking for 'הצג מחירים' buttons...")

        for attempt in range(3):
            try:
                show_buttons = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_all_elements_located(self.SHOW_PRICES_BUTTONS)
                )

                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(self.SHOW_PRICES_BUTTONS)
                )

                logging.info(f"🔍 Found {len(show_buttons)} 'הצג מחירים' buttons.")
                show_buttons[0].click()
                logging.info("🛏️ Clicked 'הצג מחירים' via native click.")
                return
            except Exception as e:
                logging.warning(f"⌛ Attempt {attempt + 1}: 'הצג מחירים' buttons not yet present or not clickable.")
                time.sleep(5)

        try:
            show_buttons = self.driver.find_elements(*self.SHOW_PRICES_BUTTONS)
            if show_buttons:
                self.driver.execute_script("arguments[0].click();", show_buttons[0])
                logging.info("⚙️ Clicked 'הצג מחירים' via JavaScript fallback.")
            else:
                raise Exception("❌ 'הצג מחירים' button never became visible.")
        except Exception as e:
            logging.error(f"❌ Failed to click 'הצג מחירים': {e}")
            raise

    def click_first_book_room(self):
        try:
            # Wait for presence of any 'book room' button
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[normalize-space()='להזמנת חדר']")
            ))

            # Use JS to ensure visibility & clickability
            clicked_text = self.driver.execute_script("""
                const buttons = Array.from(document.querySelectorAll("button"));
                const target = buttons.find(b => b.textContent.trim() === "להזמנת חדר" && b.offsetParent !== null);
                if (target) {
                    target.scrollIntoView({block: "center"});
                    target.click();
                    return target.textContent.trim();
                }
                return null;
            """)
            if clicked_text:
                logging.info(f"🏨 Clicked 'להזמנת חדר' button via JS: {clicked_text}")
            else:
                raise Exception("No visible 'להזמנת חדר' button found.")
        except Exception as e:
            logging.error(f"❌ JavaScript click failed for 'להזמנת חדר': {e}")
            raise

    def no_results_found(self) -> bool:
        try:
            banner = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(),'לא נמצאו מלונות')]"))
            )
            if banner.is_displayed():
                logging.warning("🚫 No hotels matched the search.")
                return True
            return False
        except:
            return False

    def click_book_room_button(self):
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'להזמנת חדר')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            button.click()
            logging.info("✅ Clicked 'להזמנת חדר' button.")
        except Exception as e:
            logging.error(f"❌ Could not click 'להזמנת חדר': {e}")
            raise

    def wait_for_prices_to_load(self):
        logging.info("⏳ Waiting for hotel details page to fully load...")

        retries = 2
        for attempt in range(retries):
            try:
                # Wait for the button with part of the ID (ignoring the dynamic 'NaN' part)
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(@id, 'room-price-button')]"))
                )
                # Wait for visibility of the button
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//button[contains(@id, 'room-price-button')]"))
                )
                logging.info("✅ 'הצג מחירים' button is visible.")
                return
            except Exception as e:
                logging.warning(f"⚠️ Attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    logging.info("🔁 Retrying after short wait...")
                else:
                    logging.error(f"❌ Timeout or stale element on last attempt: {e}")
                    raise




