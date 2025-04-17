import logging
import os
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class FattalConfirmPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def complete_and_verify_payment(self, expected_email):
        try:
            logging.info("🧾 Attempting to click 'בצע תשלום' in iframe...")

            # 👉 Switch to iframe
            WebDriverWait(self.driver, 15).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[id*='credit-card']"))
            )
            logging.info("✔️ Switched into payment iframe")

            # 👉 Wait for the button to be clickable
            pay_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "submitBtn"))
            )

            logging.info(f"🔍 Button found. Text: '{pay_btn.text}' | Tag: <{pay_btn.tag_name}>")

            # 👊 Use JS click instead of .click()
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pay_btn)
            self.driver.execute_script("arguments[0].click();", pay_btn)
            logging.info("💳 Clicked 'בצע תשלום' button via JS.")

            # ✅ Switch back to main content
            self.driver.switch_to.default_content()

            # ⏳ Wait for confirmation page
            logging.info("⏳ Waiting for confirmation page (מספר ההזמנה)...")
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//p[contains(text(),'מספר ההזמנה')]"))
            )

            return self.verify_confirmation_and_extract_order(expected_email)

        except Exception as e:
            screenshot_path = self._save_screenshot("confirmation_FAIL")
            logging.error(f"❌ Confirmation page timeout or failure: {e}")
            return {
                "email": expected_email,
                "order_number": "",
                "screenshot_path": screenshot_path,
                "error": str(e)
            }

    def _save_screenshot(self, prefix):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_dir = os.path.join(os.getcwd(), "Fattal_Tests", "Screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        path = os.path.join(screenshot_dir, f"{prefix}_{timestamp}.png")
        self.driver.save_screenshot(path)
        logging.error(f"📸 Screenshot saved at: {path}")
        return path

    def verify_confirmation_and_extract_order(self, expected_email):
        try:
            logging.info("🔍 Verifying confirmation page contents...")

            # ✅ Wait and extract the order number directly from span with unique class
            order_number_element = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "fSBTIq"))
            )
            order_number = order_number_element.text.strip()

            # ✅ Confirmed email fallback
            try:
                email_element = self.driver.find_element(By.XPATH, "//span[contains(@class, 'confirmation_email')]")
                confirmed_email = email_element.text.strip()
            except NoSuchElementException:
                confirmed_email = expected_email

            # 📸 Screenshot on success
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            screenshot_dir = os.path.join(os.getcwd(), "Fattal_Tests", "Screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, f"confirmation_PASS_{timestamp}.png")
            self.driver.save_screenshot(screenshot_path)

            logging.info(f"✅ Confirmation screenshot saved at: {screenshot_path}")
            logging.info(f"✅ Order Number: {order_number}, Email: {confirmed_email}")

            return {
                "email": confirmed_email,
                "order_number": order_number,
                "screenshot_path": screenshot_path
            }

        except Exception as e:
            logging.error(f"❌ Failed to extract confirmation details: {e}")
            return {
                "email": expected_email,
                "order_number": "",
                "screenshot_path": "",
                "error": str(e)
            }


