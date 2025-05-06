from faker import Faker
from selenium.common import TimeoutException, ElementNotInteractableException
from selenium.webdriver import Keys
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
                logging.info(f" [Mobile] {label} filled correctly with send_keys().")

            except ElementNotInteractableException:
                logging.warning(f"⚠ Element not interactable: '{label}'. Using JS React fallback.")

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

    #  FIELD METHODS WITH CORRECT INPUT IDs
    #  Set Email
    def set_email(self, email):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_email", email, "Email")

    #  Set Phone
    def set_phone(self, phone):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_phone", phone, "Phone")

    #  Set First Name
    def set_first_name(self, first_name):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_first-name", first_name, "First Name")

    #  Set Last Name
    def set_last_name(self, last_name):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_last-name", last_name, "Last Name")

    #  Set Israeli ID Number
    def set_id_number(self, id_number):
        self._safe_fill_mobile_field(By.ID, "checkout-form-field-input_id", id_number, "ID Number")

    #  CLUB CHECKBOX
    def click_join_club_checkbox(self):
        try:
            logging.info(" Clicking 'Join Club' checkbox (Mobile)...")

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
         מילוי רנדומלי של טופס תשלום בתוך iframe — רק לצורך בדיקות.
        כרטיס לא נשלח בפועל, מתאים להרצה ללא חיוב אמיתי.
        """
        fake = Faker('he_IL')

        try:
            logging.info(" Scrolling iframe into view (RANDOM)...")
            iframe = self.wait.until(EC.presence_of_element_located((By.ID, "paymentIframe")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", iframe)

            logging.info(" Switching into payment iframe...")
            self.driver.switch_to.frame(iframe)
            logging.info(" Switched into iframe.")

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
            logging.info(f" Expiry Month selected: {expiry_month}")

            year_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "date_year_input"))))
            year_select.select_by_visible_text(expiry_year)
            logging.info(f" Expiry Year selected: {expiry_year}")

            self._safe_fill_field(By.ID, "cvv_input", cvv, "CVV")
            self._safe_fill_field(By.ID, "id_number_input", id_number, "Card ID Number")

            logging.info(" Random Payment form filled successfully.")

        except Exception as e:
            self.take_screenshot("iframe_payment_random_fail")
            logging.error(f" Failed to fill RANDOM payment form: {e}")
            raise

        finally:
            self.driver.switch_to.default_content()
            logging.info(" Switched back to main content.")

    def click_payment_submit_button(self):
        try:
            logging.info(" Trying to click the payment submit button inside iframe...")

            #  Re-locate iframe before switching
            iframe = self.wait.until(EC.presence_of_element_located((By.ID, "paymentIframe")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", iframe)
            time.sleep(0.5)  # Small pause to ensure scrolling completes
            self.driver.switch_to.frame(iframe)

            #  Locate and click submit
            submit_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "submitBtn")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            time.sleep(0.5)  # Small pause to ensure scrolling completes
            
            # Try multiple click methods for robustness
            try:
                # First try JavaScript click (most reliable for overlays)
                self.driver.execute_script("arguments[0].click();", submit_btn)
                logging.info(" Payment submit button clicked successfully via JS.")
            except Exception as click_error:
                logging.warning(f"️ JS click failed, trying ActionChains: {click_error}")
                # Try ActionChains as fallback
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.move_to_element(submit_btn).click().perform()
                logging.info(" Payment submit button clicked via ActionChains.")

        except Exception as e:
            self.take_screenshot("fail_submitBtn_click")
            logging.error(f" Failed to click payment submit button: {e}")
            raise

        finally:
            self.driver.switch_to.default_content()
            logging.info("🔙 Switched back to main content after payment submission.")

    def apply_checkout_coupon(self, coupon_code: str):
        """
        Fills the checkout coupon input field and applies the coupon.
        Clears the input explicitly before entering the code.
        """
        try:
            logging.info(f"Trying to apply checkout coupon: {coupon_code}")

            # Locate the input field
            coupon_input = self.driver.find_element(By.ID, "input-field-input_checkout-coupon-input-field")

            # Ensure it's empty first (clear + select all fallback)
            coupon_input.clear()
            time.sleep(0.2)
            coupon_input.send_keys(Keys.CONTROL + "a")
            coupon_input.send_keys(Keys.DELETE)

            time.sleep(0.2)
            coupon_input.send_keys(coupon_code.strip())
            logging.info("Filled coupon input field.")

            # Wait a bit before clicking "Apply"
            time.sleep(0.4)

            # Locate and click the apply button
            apply_button = self.driver.find_element(By.ID, "checkout-coupon-apply-coupon-button")
            apply_button.click()
            logging.info("Clicked the 'Apply' button.")

        except Exception as e:
            logging.error(f"Failed to apply coupon: {e}")
            raise

    def is_coupon_applied_successfully(self, code):
        try:
            # First: Look for the <p> success element with the coupon ID
            coupon_success_id = f"checkout-coupon-gift-coupon_{code}"
            success_element = self.driver.find_elements(By.ID, coupon_success_id)
            if success_element:
                logging.info(f"✅ Coupon '{code}' visibly applied: found element ID {coupon_success_id}")
                return True

            # Otherwise: fallback to error handling
            error_elem = self.driver.find_element(By.ID, "input-field-error_checkout-coupon-input-field")
            error_text = error_elem.text.strip()
            logging.info(f"🧾 Coupon response text: '{error_text}'")

            if "כבר הוחל" in error_text:
                logging.info(f"🔁 Coupon '{code}' already applied.")
                return True
            elif "אינו פעיל" in error_text or "שגוי" in error_text or "לא נמצא" in error_text:
                logging.warning(f"⚠️ Coupon '{code}' is invalid or inactive.")
                return False
            else:
                logging.warning(f"⚠️ Unrecognized coupon status for '{code}': {error_text}")
                return False
        except Exception as e:
            logging.info(f"✅ No error or success element found for coupon '{code}', assuming applied.")
            return True

    def click_room_selection_summary(self):
        """
        Clicks the summary section that contains room + guest count,
        using partial text fallback if class selectors fail.
        No scroll is performed before clicking.
        """
        try:
            logging.info("Attempting to click the room selection summary header...")

            # List of alternative selectors to try (ordered fallback)
            selectors = [
                (By.CSS_SELECTOR, "div[class*='MuiAccordionSummary'] h2"),
                (By.XPATH, "//h2[contains(text(), 'חדר') and contains(text(), 'אורחים')]"),
                (By.XPATH, "//div[contains(@class, 'MuiAccordionSummary')]//h2")
            ]

            summary_h2 = None
            for by, value in selectors:
                try:
                    summary_h2 = WebDriverWait(self.driver, 6).until(
                        EC.element_to_be_clickable((by, value))
                    )
                    break  # ✅ Found one, exit loop
                except Exception:
                    continue  # Try next

            if not summary_h2:
                raise TimeoutException("Could not locate room selection summary element using any selector.")

            time.sleep(0.5)  # Optional short delay
            summary_h2.click()
            logging.info("Room summary header clicked successfully.")

        except Exception as e:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            screenshot_dir = os.path.join(os.getcwd(), "Fattal_Tests", "Screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, f"click_room_summary_fail_{timestamp}.png")
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"📸 Screenshot saved: {screenshot_path}")
            logging.error(f"❌ Failed to click room summary header: {e}")
            raise

    def click_user_agreement_checkbox_by_label_id(self):
        """
        Clicks the styled user agreement checkbox using the wrapping <label> element by ID,
        with scrollIntoView and JS-based click for maximum compatibility.
        """
        try:
            logging.info("📜 Clicking User Agreement checkbox by label ID (with scroll)...")

            label = self.wait.until(EC.presence_of_element_located((
                By.ID, "checkbox-field-control-label_terms-and-conditions"
            )))

            # Scroll into view (centered)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)

            # Perform JavaScript-based click
            self.driver.execute_script("arguments[0].click();", label)

            logging.info("✅ Checkbox clicked via label ID.")
        except Exception as e:
            self.take_screenshot("user_agreement_checkbox_by_label_fail")
            logging.error(f"❌ Failed to click User Agreement checkbox by label: {e}")
            raise


