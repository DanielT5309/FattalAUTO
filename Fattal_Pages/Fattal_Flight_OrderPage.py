import time
import logging
from selenium.common import TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class FattalFlightOrderPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # ✈️ Edit buttons for departure & return
    def click_edit_departure_flight(self):
        logging.info("🛫 Clicking 'עריכה' for departure flight")
        edit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(),'עריכה')]")
        if edit_buttons and len(edit_buttons) >= 1:
            edit_buttons[0].click()
        else:
            raise Exception("❌ Departure edit button not found")

    def click_edit_return_flight(self):
        logging.info("🛬 Clicking 'עריכה' for return flight")
        edit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(),'עריכה')]")
        if edit_buttons and len(edit_buttons) >= 2:
            edit_buttons[1].click()
        else:
            raise Exception("❌ Return edit button not found")

    def choose_first_departure_option(self):
        logging.info("📍 Selecting first departure option")
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.sc-a5db3e2f-0")))
            radio_buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                "input.PrivateSwitchBase-input[type='radio']"
            )
            if radio_buttons:
                self.driver.execute_script("arguments[0].click();", radio_buttons[0])
                logging.info("✅ Clicked departure radio button via JS.")
            else:
                raise Exception("🚫 No departure radio buttons found.")
        except Exception as e:
            logging.error(f"❌ Failed to select departure flight: {e}")
            self.take_screenshot("departure_flight_fail")
            raise

    def choose_first_return_option(self):
        logging.info(" Selecting first return option")
        try:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.sc-a5db3e2f-0")))
            radio_buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div.sc-a5db3e2f-0 .MuiRadio-root input[type='radio']"
            )
            if len(radio_buttons) >= 2:
                self.driver.execute_script("arguments[0].click();", radio_buttons[1])
                logging.info("✅ Clicked return radio button via JS.")
            else:
                raise Exception(" Less than 2 radio buttons found for return flight.")
        except Exception as e:
            logging.error(f"❌ Failed to select return flight: {e}")
            self.take_screenshot("return_flight_fail")
            raise

    def confirm_flight_selection(self):
        logging.info(" Confirming flight selection")
        button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'המשך')]"))
        )
        button.click()

    def close_flight_overlay_if_present(self):
        try:
            logging.info(" Checking for flight overlay close button...")
            close_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='סגור']"))
            )
            close_button.click()
            logging.info(" Flight overlay/modal closed.")
        except TimeoutException:
            logging.info("⏭️ No flight overlay detected, continuing.")
        except Exception as e:
            logging.warning(f" Could not close flight overlay: {e}")

    #  Handle modal if still visible
    EDIT_BUTTON = (By.XPATH, "//button[normalize-space()='עריכה']")

    def click_edit_if_present(self):
        try:
            logging.info(" Checking for lingering confirmation modal...")
            edit_button = self.wait.until(EC.presence_of_element_located(self.EDIT_BUTTON))
            if edit_button.is_displayed():
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_button)
                edit_button.click()
                logging.info(" 'עריכה' clicked to clear modal.")
        except Exception as e:
            logging.warning(f" 'עריכה' not present or already dismissed: {e}")

    def take_screenshot(self, name):
        filename = f"Screenshots/{name}_{int(time.time())}.png"
        self.driver.save_screenshot(filename)
        logging.info(f" Screenshot saved to {filename}")

    def try_flight_options_by_time_of_day(self):
        time_tabs = ['בוקר', 'צהריים', 'ערב']
        attempt = 1

        for label in time_tabs:
            logging.info(f"🕒 Attempting flight booking with time tab: {label} (Attempt {attempt})")
            try:
                self.select_time_tab(label)

                self.click_edit_departure_flight()
                self.choose_first_departure_option()

                self.click_edit_return_flight()
                if not self.has_enough_return_options(min_required=2):
                    raise Exception("Less than 2 return radio buttons found.")

                self.choose_first_return_option()
                #self.confirm_flight_selection()

                current_url = self.driver.current_url
                logging.info(f"🌍 Current URL after flight confirm: {current_url}")

                if self.ensure_passenger_form_loaded():
                    logging.info(f"🎉 Flight selection successful with tab: {label}")
                    return True
                else:
                    raise Exception("Passenger form did not load")

            except Exception as e:
                logging.warning(f"❌ Time tab '{label}' failed: {e}")
                self.click_edit_if_present()
                attempt += 1
                continue

        logging.warning("⚠️ All time tab attempts failed. Manual flight selection may be required.")
        return False

    def handle_passenger_form_if_flight_selection_skipped(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'פרטי הטסים')]"))
            )
            logging.info("🧍 Passenger form is present, not skipped.")
            return False
        except TimeoutException:
            logging.info("✈️ Passenger form is not visible. Assuming flight form was skipped.")
            return True

    def fill_passenger_details(self):
        logging.info(" Filling passenger details (2 adults, 1 child, 1 infant)...")
        try:
            self.wait.until(lambda d: len(
                d.find_elements(By.XPATH, "//input[@id='checkout.personal_details_form.label_first_name']")) >= 4)
            logging.info(" Passenger form is ready.")

            first_names = ["John", "Jane", "Tom", "Baby"]
            last_names = ["Test", "Test", "Test", "Test"]
            birthdate = "01/01/2015"
            infant_birthdate = "01/01/2024"

            def type_passenger(index, label, dob=None, dob_position=None):
                first = self.driver.find_element(
                    By.XPATH, f"(//input[@id='checkout.personal_details_form.label_first_name'])[{index}]")
                self.scroll_and_type(first, first_names[index - 1])
                logging.info(f" {label} First Name filled.")

                last = self.driver.find_element(
                    By.XPATH, f"(//input[@id='checkout.personal_details_form.label_last_name'])[{index}]")
                self.scroll_and_type(last, last_names[index - 1])
                logging.info(f" {label} Last Name filled.")

                if dob and dob_position is not None:
                    dob_fields = self.driver.find_elements(
                        By.XPATH, "//input[@id='checkout.personal_details_form.label_birthDate']")
                    if len(dob_fields) > dob_position:
                        dob_field = dob_fields[dob_position]
                        self.scroll_and_type(dob_field, dob)
                        self.driver.execute_script("arguments[0].blur();", dob_field)
                        logging.info(f"{label} Birthdate filled.")
                    else:
                        logging.warning(f" No DOB field for {label} at expected position {dob_position}")

            type_passenger(1, "מבוגר1")
            type_passenger(2, "מבוגר2")
            type_passenger(3, "ילד", dob=birthdate, dob_position=0)
            type_passenger(4, "תינוק", dob=infant_birthdate, dob_position=1)

            logging.info(" All passenger fields filled successfully.")

        except Exception as e:
            self.take_screenshot("fill_passenger_details_error")
            logging.error(f" Failed to fill passenger form: {e}")
            raise

    def click_continue_button(self):
        try:
            continue_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'המשך')]"))
            )
            time.sleep(0.5)
            continue_btn.click()
            logging.info(" Clicked continue button.")
        except Exception as e:
            logging.error(f" Could not click 'continue' button: {e}")
            raise

    def select_time_tab(self, label_text):
        try:
            logging.info(f"🔄 Attempting to switch to time tab: {label_text}")
            tab_button = self.driver.find_element(By.XPATH, f"//button[contains(.,'{label_text}')]")
            self.driver.execute_script("arguments[0].click();", tab_button)
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f"//button[text()='{label_text}']"))
            )
            logging.info(f"✅ Time tab '{label_text}' is open and ready.")
            time.sleep(0.8)
        except Exception as e:
            logging.warning(f"⚠️ Could not click time tab '{label_text}': {e}")

    def scroll_and_type(self, element, value):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.wait.until(EC.visibility_of(element))
            self.wait.until(lambda d: element.is_enabled())
            self.driver.execute_script("arguments[0].focus();", element)
            time.sleep(0.3)
            element.clear()
            element.send_keys(value)
        except ElementNotInteractableException as e:
            logging.warning(f" Element not interactable, retrying in 0.7s... {e}")
            time.sleep(0.7)
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                self.driver.execute_script("arguments[0].focus();", element)
                time.sleep(0.3)
                element.clear()
                element.send_keys(value)
            except Exception as e2:
                raise ElementNotInteractableException(f"Still not interactable after retry: {e2}")

    def fill_passenger_details_and_validate(self):
        try:
            self.fill_passenger_details()
        except Exception as e:
            logging.error(f" Failed to fill passenger form: {e}")
            self.take_screenshot("fill_passenger_form_fail")
            raise

        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.continue")))
            logging.info(" Continue button is present")
        except Exception:
            logging.warning(" Continue button not found — may not have rendered")

        try:
            errors = self.driver.find_elements(By.CSS_SELECTOR, ".Mui-error")
            if errors:
                logging.warning(f" Form contains {len(errors)} validation errors before clicking continue!")
                for err in errors:
                    logging.warning(f" Error: {err.text}")
        except Exception:
            logging.debug(" No visible form validation errors detected.")

    def wait_for_passenger_form(self):
        logging.info(" Waiting for passenger form to be ready...")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'פרטי הטסים')]"))
        )
        logging.info(" Passenger form is loaded.")

    def has_enough_return_options(self, min_required=2):
        try:
            radios = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//input[@type='radio']"))
            )
            return len(radios) >= min_required
        except TimeoutException:
            return False

    def ensure_passenger_form_loaded(self):
        try:
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'פרטי הטסים')]"))
            )
            logging.info("🧍 Passenger form is present.")
            return True
        except TimeoutException:
            logging.warning("😬 Passenger form NOT loaded after flight confirmation.")
            return False
