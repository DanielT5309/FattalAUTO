import random
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
import logging

class FattalOrderPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def _safe_fill_field(self, by, value, text, label):
        try:
            el = self.wait.until(EC.presence_of_element_located((by, value)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            if el.is_enabled():
                el.clear()
                el.send_keys(text)
                logging.info(f"✅ {label} set: {text}")
            else:
                logging.info(f"ℹ️ {label} field is disabled, skipping input.")
        except Exception as e:
            logging.warning(f"⚠️ Standard method failed for {label}, falling back to JS: {e}")
            self._fallback_set_by_js(text, label)

    def set_email(self, email):
        try:
            self._safe_fill_field(By.ID, "checkout-form-field-input_email", email, "Email")
        except:
            self._safe_fill_field(By.ID, "checkout.personal_details_form.label_email", email, "Email")

    def set_phone(self, phone):
        try:
            self._safe_fill_field(By.ID, "checkout-form-field-input_phone", phone, "Phone")
        except:
            self._safe_fill_field(By.ID, "checkout.personal_details_form.label_phone", phone, "Phone")

    def set_first_name(self, name):
        try:
            self._safe_fill_field(By.ID, "checkout-form-field-input_first-name", name, "First name")
        except:
            self._safe_fill_field(By.ID, "checkout.personal_details_form.label_first_name", name, "First name")

    def set_last_name(self, name):
        try:
            self._safe_fill_field(By.ID, "checkout-form-field-input_last-name", name, "Last name")
        except:
            self._safe_fill_field(By.ID, "checkout.personal_details_form.label_last_name", name, "Last name")

    def set_id_number(self, id_number):
        try:
            self._safe_fill_field(By.ID, "checkout-form-field-input_id", id_number, "ID number")
        except:
            self._safe_fill_field(By.ID, "checkout.personal_details_form.label_id", id_number, "ID number")

    def _fallback_set_by_js(self, text, label):
        script = f"""
            const inputs = Array.from(document.querySelectorAll('input'));
            const target = inputs.find(i => 
                i.id?.includes('{label.lower()}') || 
                i.placeholder?.includes('{label}') || 
                i.name?.includes('{label.lower()}')
            );
            if (target) {{
                target.scrollIntoView({{block: 'center'}});
                target.value = '{text}';
                target.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return true;
            }}
            return false;
        """
        result = self.driver.execute_script(script)
        if result:
            logging.info(f"✅ {label} set via JS fallback.")
        else:
            logging.error(f"❌ Failed to set {label} even via JS.")

    def wait_until_personal_form_ready(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.ID, "checkout-personal-details-content")))
            logging.info("🕐 Order form is ready (new structure).")
        except:
            try:
                self.wait.until(EC.visibility_of_element_located((By.ID, "checkout.personal_details_form.label_email")))
                logging.info("🕐 Order form is ready (old structure).")
            except Exception as e:
                logging.error(f"❌ Payment form not ready: {e}")
                raise

    def club_checkbox(self):
        try:
            # Click the visible part of the checkbox (not the hidden input)
            checkbox_label = self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "label.MuiFormControlLabel-root span.MuiButtonBase-root"
            )))

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox_label)
            self.wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "label.MuiFormControlLabel-root span.MuiButtonBase-root"
            ))).click()

            logging.info("✅ Club checkbox clicked successfully.")

        except Exception as e:
            logging.error(f"❌ Failed to click club checkbox: {e}")
            raise

    def get_late_checkout_checkbox(self):
        return self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[text()='עזיבה מאוחרת']/ancestor::label//input")))

    def get_high_floor_checkbox(self):
        return self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[text()='קומה גבוהה']/ancestor::label//input")))

    def get_low_floor_checkbox(self):
        return self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[text()='קומה נמוכה']/ancestor::label//input")))

    def get_adjacent_rooms_checkbox(self):
        return self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[text()='חדרים צמודים']/ancestor::label//input")))

    def get_special_request_textarea(self):
        return self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "textarea[name='custom']")))

    def click_terms_approval_checkbox_js(self):
        try:
            logging.info("🕵️ Locating and clicking 'terms approval' checkbox...")

            label = self.wait.until(EC.presence_of_element_located((By.XPATH,
                "//label[contains(., 'אני מאשר') and .//input[@type='checkbox']]"
            )))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)

            clicked = self.driver.execute_script("""
                const checkbox = Array.from(document.querySelectorAll("label"))
                    .find(el => el.innerText.includes("אני מאשר") && el.querySelector("input[type='checkbox']"))
                    ?.querySelector("input[type='checkbox']");
                if (checkbox && !checkbox.checked) {
                    checkbox.click();
                    return true;
                }
                return checkbox?.checked || false;
            """)

            if clicked:
                logging.info("✔️ Checkbox clicked successfully (via JS)")
            else:
                raise Exception("Checkbox not found or already checked.")

        except Exception as e:
            logging.error(f"❌ Failed to click terms approval checkbox: {e}")
            raise

    def get_marketing_consent_checkbox(self):
        return self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[contains(text(),'קבלת דברי פרסומת')]/ancestor::label//input")))

    def set_card_number(self, card_number):
        self._safe_fill_field(By.ID, "credit_card_number_input", card_number, "Card number")

    def set_cardholder_name(self, name):
        self._safe_fill_field(By.ID, "card_holder_name_input", name, "Cardholder name")

    def select_expiry_month(self, value: str):
        try:
            select_el = self.wait.until(EC.presence_of_element_located((By.ID, "date_month_input")))
            Select(select_el).select_by_visible_text(value.zfill(2))
            logging.info(f"✅ Expiry month selected: {value.zfill(2)}")
        except Exception as e:
            logging.error(f"❌ Failed to select expiry month: {e}")
            raise

    def select_expiry_year(self, value: str):
        try:
            select_el = self.wait.until(EC.presence_of_element_located((By.ID, "date_year_input")))
            Select(select_el).select_by_visible_text(value)
            logging.info(f"✅ Expiry year selected: {value}")
        except Exception as e:
            logging.error(f"❌ Failed to select expiry year: {e}")
            raise

    def set_cvv(self, cvv):
        self._safe_fill_field(By.ID, "cvv_input", cvv, "CVV")

    def set_id_number_card(self, id_number):
        self._safe_fill_field(By.ID, "id_number_input", id_number, "Card ID number")

    def click_submit_button(self):
        try:
            logging.info(" Trying to click the payment submit button inside iframe...")

            # Re-locate and switch into the iframe
            iframe = self.wait.until(EC.presence_of_element_located((By.ID, "paymentIframe")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", iframe)
            self.driver.switch_to.frame(iframe)
            logging.info(" Switched into iframe.")

            # Wait for the button with retry logic
            retries = 3
            for attempt in range(retries):
                try:
                    submit_btn = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "submitBtn"))
                    )
                    logging.info(f" Found submit button on attempt {attempt + 1}")
                    break
                except TimeoutException as e:
                    logging.warning(f" Attempt {attempt + 1} failed — retrying...")
            else:
                raise TimeoutException(" Submit button not found after retries.")

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)

            # Try JS click first
            try:
                self.driver.execute_script("arguments[0].click();", submit_btn)
                logging.info(" Payment submit button clicked via JS.")
            except Exception as js_error:
                logging.warning(f" JS click failed: {js_error}")
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(self.driver).move_to_element(submit_btn).click().perform()
                    logging.info(" Payment submit button clicked via ActionChains.")
                except Exception as ac_error:
                    raise Exception(f" Both JS and ActionChains failed: {ac_error}")

        except Exception as final_error:
            logging.error(f" Failed to click submit button: {final_error}")
            raise Exception(f" Submit click failed completely: {final_error}")

        finally:
            self.driver.switch_to.default_content()
            logging.info(" Switched back to main content after payment submission.")

    def expand_special_requests_section(self):
        try:
            toggle_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//h2[contains(text(),'בקשות מיוחדות')]/ancestor::div[contains(@class,'MuiAccordionSummary-root')]")
            ))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", toggle_button)
            toggle_button.click()
            logging.info("📬 Expanded special requests section")
        except Exception as e:
            logging.error(f"❌ Failed to expand special requests section: {e}")
            raise

    def switch_to_payment_iframe(self):
        try:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "paymentIframe")))
            logging.info("✔️ Switched into payment iframe")
        except Exception as e:
            logging.error(f"❌ Could not switch into payment iframe: {e}")
            raise

    def switch_to_default_content(self):
        self.driver.switch_to.default_content()
        logging.info("↩️ Switched back to default content")

    def validate_israeli_id(self, id_number):
        id_number = str(id_number)
        if len(id_number) != 9 or not id_number.isdigit():
            return False
        digits = [int(digit) for digit in id_number]
        for i in range(7, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        return sum(digits) % 10 == 0

    # Function to generate a random valid Israeli ID
    def generate_israeli_id(self):
        while True:
            id_number = str(random.randint(100000000, 999999999))  # Generate a random 9-digit number
            if self.validate_israeli_id(id_number):  # Validate that the ID is correct
                return id_number
            # Repeat until a valid ID is generated

    # Example method for setting ID number in the order form
    def set_random_israeli_id(self):
        random_id = self.generate_israeli_id()  # Generate a random valid ID
        logging.info(f"Generated Israeli ID: {random_id}")

        # Now set the generated ID on the order form
        self.set_id_number(random_id)

