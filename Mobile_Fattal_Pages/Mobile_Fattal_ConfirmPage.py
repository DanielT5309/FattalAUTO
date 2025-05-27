import logging
import os
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class FattalMobileConfirmPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def complete_and_verify_payment(self, expected_email):
        try:
            logging.info("Mobile: Attempting to click 'בצע תשלום' in iframe...")

            # Switch to iframe (mobile may have dynamic ID or name)
            WebDriverWait(self.driver, 15).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[id*='credit-card'], iframe[name*='paymentIframe']"))
            )
            logging.info("Switched into mobile payment iframe")

            # Wait and click 'submitBtn'
            submit_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "submitBtn")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            self.driver.execute_script("arguments[0].click();", submit_btn)
            logging.info("Clicked 'בצע תשלום' button via JS (Mobile).")

            # Back to main content
            self.driver.switch_to.default_content()

            # Wait for confirmation element to load
            logging.info("Waiting for confirmation page (מספר ההזמנה)...")
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//p[contains(text(),'מספר ההזמנה')]"))
            )

            return self.verify_confirmation_and_extract_order(expected_email)

        except Exception as e:
            screenshot_path = self._save_screenshot("mobile_confirmation_FAIL")
            logging.error(f"Mobile confirmation page timeout or failure: {e}")
            return {
                "email": expected_email,
                "order_number": "",
                "screenshot_path": screenshot_path,
                "error": str(e)
            }

    def verify_confirmation_and_extract_order_mobile(self):
        try:
            logging.info("Waiting for mobile confirmation page to load...")

            # Wait up to 20 seconds for the page to display confirmation container
            WebDriverWait(self.driver, 20, poll_frequency=0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[id='thank-you-page-top-bar-text'], .fSBTIq"))
            )
            logging.info("Confirmation page detected — now waiting for order number element...")

            # Now wait specifically for the order number element
            order_number_element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "fSBTIq"))
            )
            order_number = order_number_element.text.strip()

            # Screenshot
            screenshot_path = self._save_screenshot("confirmation_PASS")

            logging.info(f"Confirmation screenshot saved at: {screenshot_path}")
            logging.info(f"Order Number (mobile): {order_number}")

            return {
                "order_number": order_number,
                "screenshot_path": screenshot_path
            }

        except Exception as e:
            screenshot_path = self._save_screenshot("confirmation_FAIL")
            logging.error(f"❌ Failed to extract confirmation (mobile): {e}")
            return {
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
        logging.info(f"Screenshot saved at: {path}")
        return path


