import time
import logging
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver


class FattalMobileCustomerSupport:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def safe_click(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            element.click()
        except Exception:
            logging.warning("Regular click failed. Trying JS click with mousedown event...")
            self.driver.execute_script("""
                const evt = new MouseEvent('mousedown', { bubbles: true });
                arguments[0].dispatchEvent(evt);
                arguments[0].click();
            """, element)
            time.sleep(0.5)

    def click_send_us_inquiry_button(self):
        try:
            logging.info("Clicking 'שלחו לנו פנייה' button...")
            button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'שלחו לנו פנייה') or contains(text(),'שלחנו לנו פנייה')]"))
            )
            self.safe_click(button)
            logging.info("'שלחו לנו פנייה' clicked.")
        except Exception as e:
            logging.error(f"Failed to click inquiry button: {e}")
            raise

    def fill_basic_contact_fields(self, first_name, last_name, id_number, phone, email, message, accept_marketing=False):
        try:
            logging.info("Filling basic contact fields...")

            def fill_input_by_label(label_text, value):
                xpath = f"//label[contains(text(), '{label_text}')]/following-sibling::input"
                input_field = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_field)
                input_field.clear()
                input_field.send_keys(value)
                logging.info(f"Filled: {label_text}")

            fill_input_by_label("שם פרטי", first_name)
            fill_input_by_label("שם משפחה", last_name)
            fill_input_by_label("תעודת זהות", id_number)
            fill_input_by_label("מספר טלפון", phone)
            fill_input_by_label("כתובת אימייל", email)

            self.driver.execute_script("if(document.activeElement) document.activeElement.blur();")
            time.sleep(0.5)

            textarea = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[name='custom']")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textarea)
            textarea.clear()
            textarea.send_keys(message)
            logging.info("Filled message textarea.")

            if accept_marketing:
                checkbox = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']")))
                if not checkbox.is_selected():
                    self.driver.execute_script("arguments[0].click();", checkbox)
                logging.info("Marketing checkbox selected.")

        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = os.path.join("Fattal_Tests", "Screenshots", f"fill_fields_error_{timestamp}.png")
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"Failed to fill fields. Screenshot saved: {screenshot_path}")
            raise

    def select_dropdown_by_label(self, label_text, option_text=None):
        try:
            logging.info(f"Selecting dropdown by visible label: {label_text}")

            # Find the visible label element
            label_div_xpath = f"//div[text()[normalize-space()='{label_text}']]"
            label_div = self.wait.until(EC.presence_of_element_located((By.XPATH, label_div_xpath)))

            # Now find the dropdown element following that label container
            dropdown = label_div.find_element(By.XPATH, "./following::div[@role='combobox'][1]")

            self.safe_click(dropdown)
            time.sleep(0.4)

            if option_text:
                option_xpath = f"//ul[@role='listbox']//li[contains(text(), '{option_text}')]"
            else:
                option_xpath = "//ul[@role='listbox']//li[1]"

            option = self.wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            self.safe_click(option)

            logging.info(f"Selected option from dropdown '{label_text}': {option_text or 'First option'}")

        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join("Fattal_Tests", "Screenshots", f"dropdown_fail_{label_text}_{timestamp}.png")
            self.driver.save_screenshot(path)
            logging.error(f"Failed to select from dropdown '{label_text}'. Screenshot saved: {path}")
            raise

    def click_recaptcha_checkbox(self):
        try:
            logging.info("Attempting to click reCAPTCHA checkbox...")

            # Switch to iframe containing the reCAPTCHA checkbox
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, "//iframe[contains(@title, 'reCAPTCHA')]")
            ))

            checkbox = self.wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
            self.safe_click(checkbox)
            logging.info("reCAPTCHA checkbox clicked.")

            # Switch back to main content
            self.driver.switch_to.default_content()

            # Wait for validation to complete
            time.sleep(2)

        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = os.path.join("Fattal_Tests", "Screenshots", f"recaptcha_fail_{timestamp}.png")
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"Failed to click reCAPTCHA: {e}. Screenshot saved: {screenshot_path}")
            raise

    def submit_contact_form(self):
        try:
            logging.info("Clicking Submit (שלח) button...")
            submit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'שלח')]"))
            )
            self.safe_click(submit_btn)
            logging.info("Form submitted successfully.")

        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = os.path.join("Fattal_Tests", "Screenshots", f"submit_fail_{timestamp}.png")
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"Failed to submit form: {e}. Screenshot saved: {screenshot_path}")
            raise
    def assert_form_data_matches_input(self, first_name, last_name, id_number, phone, email, message):
        try:
            logging.info("Asserting filled form data...")

            def get_input_value_by_label(label_text):
                xpath = f"//label[contains(text(), '{label_text}')]/following-sibling::input"
                input_field = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                return input_field.get_attribute("value").strip()

            assert get_input_value_by_label("שם פרטי") == first_name, "First name mismatch"
            assert get_input_value_by_label("שם משפחה") == last_name, "Last name mismatch"
            assert get_input_value_by_label("תעודת זהות") == id_number, "ID mismatch"
            assert get_input_value_by_label("מספר טלפון") == phone, "Phone mismatch"
            assert get_input_value_by_label("כתובת אימייל") == email, "Email mismatch"

            textarea = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[name='custom']")))
            actual_msg = textarea.get_attribute("value").strip()
            assert actual_msg == message, "Message content mismatch"

            logging.info("All form fields are correctly filled.")
        except AssertionError as ae:
            logging.error(f"Assertion failed: {ae}")
            raise
        except Exception as e:
            logging.error(f"Error verifying form data: {e}")
            raise


