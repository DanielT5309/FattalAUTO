import time
import logging
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class FattalMobileClubJoinPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def click_join_fattal_friends_button(self):
        """
        Scrolls to and clicks the 'להצטרפות למועדון' (Join the Club) button.
        """
        try:
            logging.info("Scrolling to and clicking 'להצטרפות למועדון' button...")

            join_button_xpath = "//a[contains(text(), 'להצטרפות למועדון')]"
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, join_button_xpath)))

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(0.3)
            button.click()

            logging.info("'להצטרפות למועדון' button clicked successfully.")

        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join("Fattal_Tests", "Screenshots", f"join_club_click_fail_{timestamp}.png")
            self.driver.save_screenshot(path)
            logging.error(f"Failed to click 'להצטרפות למועדון'. Screenshot saved: {path}")
            raise

    def fill_join_fattal_club_form(self, first_name, last_name, email, phone, id_number, birthdate="01/01/1990",
                                   password="Aa123456"):
        """
        Fills the join club form with provided guest data. Logs the ID number used.
        """
        try:
            logging.info("Filling Fattal Friends club join form...")
            logging.info(f"Using ID Number: {id_number}")

            def fill_input_by_label(label_text, value):
                xpath = f"//label[contains(text(), '{label_text}')]/following-sibling::input"
                field = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
                field.clear()
                field.send_keys(value)
                logging.info(f"Filled input: {label_text}")

            fill_input_by_label("שם פרטי", first_name)
            fill_input_by_label("שם משפחה", last_name)
            fill_input_by_label("כתובת דוא״ל", email)
            fill_input_by_label("מספר טלפון נייד", phone)
            fill_input_by_label("תאריך לידה", birthdate)
            fill_input_by_label("מספר תעודת זהות", id_number)
            fill_input_by_label("בחרו סיסמא", password)

            logging.info("All club form fields filled successfully.")

        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            screenshot = os.path.join("Fattal_Tests", "Screenshots", f"club_form_error_{timestamp}.png")
            self.driver.save_screenshot(screenshot)
            logging.error(f"Error while filling club form. Screenshot saved: {screenshot}")
            raise

    def assert_input_value(self, label_text, expected_value):
        xpath = f"//label[contains(text(), '{label_text}')]/following-sibling::input"
        field = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        actual_value = field.get_attribute("value")
        assert actual_value == expected_value, f"Value mismatch for '{label_text}': expected '{expected_value}', got '{actual_value}'"

    def click_accept_terms_checkbox(self):
        """
        Clicks the 'קראתי ואני מסכימ/ה לתקנון המועדון' checkbox using the parent span.
        """
        try:
            logging.info("Clicking the terms acceptance checkbox...")

            # Wait for the visible wrapper span that is styled as a checkbox
            checkbox_wrapper_xpath = "//span[contains(@class, 'MuiButtonBase-root') and contains(@class, 'MuiCheckbox-root')]"
            checkbox_wrapper = self.wait.until(EC.element_to_be_clickable((By.XPATH, checkbox_wrapper_xpath)))

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox_wrapper)
            time.sleep(0.3)  # Just to stabilize animation
            checkbox_wrapper.click()

            logging.info("Checkbox clicked successfully.")

        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            screenshot = os.path.join("Fattal_Tests", "Screenshots", f"checkbox_click_fail_{timestamp}.png")
            self.driver.save_screenshot(screenshot)
            logging.error(f"Failed to click checkbox. Screenshot saved: {screenshot}")
            raise

