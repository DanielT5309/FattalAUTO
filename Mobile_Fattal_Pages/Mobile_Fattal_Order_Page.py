from faker import Faker
from selenium.common import TimeoutException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import random
import logging
from datetime import datetime
import os
from selenium.webdriver.support.ui import Select

class FattalOrderPageMobile:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def take_screenshot(self, name="error_screenshot"):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_dir = os.path.join(os.getcwd(), "Screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        path = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(path)
        logging.error(f"📸 Screenshot saved: {path}")

    def wait_until_personal_form_ready(self):
        logging.info("🕐 Waiting for personal details form (mobile)...")

        try:
            def email_input_appears(driver):
                email_inputs = driver.find_elements(By.ID, "checkout-form-field-input_email")
                for el in email_inputs:
                    if el.is_displayed():
                        logging.info("✅ Email input is visible.")
                        return el
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                        time.sleep(0.4)
                        if el.is_displayed():
                            logging.info("✅ Email input became visible after scrolling.")
                            return el
                return False

            WebDriverWait(self.driver, 30).until(email_input_appears)

        except TimeoutException:
            self.take_screenshot("mobile_personal_form_timeout")
            logging.error("📸 Screenshot saved.")
            logging.error(
                "❌ Personal form did not load in time: 🛑 Could not locate visible email input after scrolling.")
            raise TimeoutException("🛑 Could not locate visible email input after scrolling.")

    def _safe_fill_mobile_field(self, by, value, text, label):
        try:
            logging.info(f"📝 Trying to fill {label} with '{text}'")
            for _ in range(8):
                elements = self.driver.find_elements(by, value)
                if elements:
                    break
                self.driver.execute_script("window.scrollBy(0, 250);")
                time.sleep(0.2)
            else:
                raise TimeoutException(f"❌ Couldn't find {label} field.")

            el = elements[0]
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            self.wait.until(lambda d: el.is_displayed() and el.is_enabled())

            try:
                # Try traditional way first
                el.click()
                el.clear()
                for _ in range(10):
                    el.send_keys("\ue003")
                    time.sleep(0.02)
                el.send_keys(text)
                logging.info(f"✅ [Mobile] {label} filled correctly with send_keys().")

            except ElementNotInteractableException:
                logging.warning(f"⚠️ Element not interactable: '{label}'. Using JS React fallback.")

                react_fallback = """
                    var el = arguments[0];
                    var value = arguments[1];
                    var lastValue = el.value;
                    el.value = value;
                    var event = new Event('input', { bubbles: true });
                    event.simulated = true;
                    var tracker = el._valueTracker;
                    if (tracker) tracker.setValue(lastValue);
                    el.dispatchEvent(event);
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                """
                self.driver.execute_script(react_fallback, el, text)
                logging.info(f"✅ JS React fallback succeeded for '{label}'")

        except Exception as e:
            self.take_screenshot(f"mobile_input_fail_{label}")
            logging.error(f"❌ Failed to set {label}: {e}")
            raise

    # ✅ FIELD METHODS WITH CORRECT INPUT IDs
    # ✅ Set Email
    def set_email(self, email):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_email", email, "Email")

    # ✅ Set Phone
    def set_phone(self, phone):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_phone", phone, "Phone")

    # ✅ Set First Name
    def set_first_name(self, first_name):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_first-name", first_name, "First Name")

    # ✅ Set Last Name
    def set_last_name(self, last_name):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_last-name", last_name, "Last Name")

    # ✅ Set Israeli ID Number
    def set_id_number(self, id_number):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_id", id_number, "ID Number")

    # ✅ CLUB CHECKBOX
    def click_join_club_checkbox(self):
        try:
            logging.info("📦 Clicking 'Join Club' checkbox (Mobile)...")

            # Try common patterns (can extend if needed)
            xpaths = [
                "//label[.//span[contains(text(),'לחדש את המועדון')]]",
                "//label[.//span[contains(text(),'להצטרף למועדון')]]",
                "//label[.//span[contains(text(),'מועדון')]]"
            ]

            for xpath in xpaths:
                try:
                    label = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                    time.sleep(0.3)
                    self.driver.execute_script("arguments[0].click();", label)
                    logging.info(f"✅ Clicked 'Join Club' checkbox using XPath: {xpath}")
                    return
                except TimeoutException:
                    continue

            raise TimeoutException("❌ Join Club checkbox not found with fallback XPaths.")

        except Exception as e:
            self.take_screenshot("join_club_checkbox_fail")
            logging.error(f"❌ Failed to click 'Join Club' checkbox: {e}")
            raise

    # ✅ USER AGREEMENT CHECKBOX
    def click_user_agreement_checkbox(self):
        try:
            logging.info("📜 Clicking 'User Agreement' checkbox (Mobile)...")
            label = self.wait.until(EC.presence_of_element_located((
                By.XPATH, "//span[contains(text(),'אני מאשר')]/ancestor::label"
            )))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
            self.driver.execute_script("arguments[0].click();", label)
            logging.info("✅ Clicked 'User Agreement' checkbox.")
        except Exception as e:
            self.take_screenshot("user_agreement_checkbox_fail")
            logging.error(f"❌ Failed to click 'User Agreement' checkbox: {e}")
            raise

    # ✅ ISRAELI ID UTILS
    def validate_israeli_id(self, id_number):
        id_number = str(id_number)
        if len(id_number) != 9 or not id_number.isdigit():
            return False
        digits = [int(d) for d in id_number]
        for i in range(7, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        return sum(digits) % 10 == 0

    def generate_israeli_id(self):
        while True:
            id_number = str(random.randint(100000000, 999999999))
            if self.validate_israeli_id(id_number):
                return id_number

    def set_random_israeli_id(self):
        id_number = self.generate_israeli_id()
        logging.info(f"🎲 Generated Israeli ID: {id_number}")
        self.set_id_number(id_number)

    def _safe_fill_field(self, by, value, text, label):
        try:
            el = self.wait.until(EC.element_to_be_clickable((by, value)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            el.clear()
            el.send_keys(text)
            logging.info(f"✅ {label} filled correctly.")
        except Exception as e:
            self.take_screenshot(f"fail_{label.replace(' ', '_')}")
            logging.error(f"❌ Failed to fill {label}: {e}")
            raise

    def fill_payment_iframe_mobile(self):
        try:
            logging.info("💳 Scrolling iframe into view...")
            iframe = self.wait.until(EC.presence_of_element_located((By.ID, "paymentIframe")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", iframe)

            logging.info("💳 Switching into payment iframe...")
            self.driver.switch_to.frame(iframe)
            logging.info("✅ Switched into iframe.")

            # Fill Card Number
            self._safe_fill_field(By.ID, "credit_card_number_input", "4580080111866879", "Card Number")

            # Fill Cardholder Name
            self._safe_fill_field(By.ID, "card_holder_name_input", "פתאל", "Cardholder Name")

            # Select Expiry Month
            month_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "date_month_input"))))
            month_select.select_by_visible_text("08")
            logging.info("✅ Expiry Month selected: 08")

            # Select Expiry Year
            year_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "date_year_input"))))
            year_select.select_by_visible_text("2025")
            logging.info("✅ Expiry Year selected: 2025")

            # Fill CVV
            self._safe_fill_field(By.ID, "cvv_input", "955", "CVV")

            # Fill ID Number
            self._safe_fill_field(By.ID, "id_number_input", "0356998", "Card ID Number")

            logging.info("🎯 Payment form filled successfully.")

        except Exception as e:
            self.take_screenshot("iframe_payment_fail")
            logging.error(f"❌ Failed to fill payment form in iframe: {e}")
            raise
        finally:
            self.driver.switch_to.default_content()
            logging.info("🔙 Switched back to main content.")

    def fill_payment_iframe_mobile_random(self):
        """
        💳 מילוי רנדומלי של טופס תשלום בתוך iframe — רק לצורך בדיקות.
        כרטיס לא נשלח בפועל, מתאים להרצה ללא חיוב אמיתי.
        """
        fake = Faker('he_IL')

        try:
            logging.info("💳 Scrolling iframe into view (RANDOM)...")
            iframe = self.wait.until(EC.presence_of_element_located((By.ID, "paymentIframe")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", iframe)

            logging.info("💳 Switching into payment iframe...")
            self.driver.switch_to.frame(iframe)
            logging.info("✅ Switched into iframe.")

            # Card number (דמו בלבד)
            card_number = "4580080111866879"
            cardholder_name = fake.name()
            expiry_month = str(random.randint(1, 12)).zfill(2)
            expiry_year = str(random.randint(2025, 2028))
            cvv = str(random.randint(100, 999))
            id_number = str(random.randint(1000000, 9999999))

            self._safe_fill_field(By.ID, "credit_card_number_input", card_number, "Card Number")
            self._safe_fill_field(By.ID, "card_holder_name_input", cardholder_name, "Cardholder Name")

            month_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "date_month_input"))))
            month_select.select_by_visible_text(expiry_month)
            logging.info(f"✅ Expiry Month selected: {expiry_month}")

            year_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "date_year_input"))))
            year_select.select_by_visible_text(expiry_year)
            logging.info(f"✅ Expiry Year selected: {expiry_year}")

            self._safe_fill_field(By.ID, "cvv_input", cvv, "CVV")
            self._safe_fill_field(By.ID, "id_number_input", id_number, "Card ID Number")

            logging.info("🎯 Random Payment form filled successfully.")

        except Exception as e:
            self.take_screenshot("iframe_payment_random_fail")
            logging.error(f"❌ Failed to fill RANDOM payment form: {e}")
            raise

        finally:
            self.driver.switch_to.default_content()
            logging.info("🔙 Switched back to main content.")

    def click_payment_submit_button(self):
        try:
            logging.info("🚀 Trying to click the payment submit button inside iframe...")

            # ✅ Re-locate iframe before switching
            iframe = self.wait.until(EC.presence_of_element_located((By.ID, "paymentIframe")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", iframe)
            self.driver.switch_to.frame(iframe)

            # ✅ Locate and click submit
            submit_btn = self.wait.until(EC.presence_of_element_located((By.ID, "submitBtn")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", submit_btn)

            logging.info("✅ Payment submit button clicked successfully via JS.")

        except Exception as e:
            self.take_screenshot("fail_submitBtn_click")
            logging.error(f"❌ Failed to click payment submit button: {e}")
            raise

        finally:
            self.driver.switch_to.default_content()
            logging.info("🔙 Switched back to main content after payment submission.")



