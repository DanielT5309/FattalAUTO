from selenium.common import TimeoutException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)


class FattalFlightPageMobile:
    def __init__(self, driver: webdriver.Chrome):
        self.wait = WebDriverWait(driver, 10)
        self.driver = driver

    # Try booking flights by time of day
    def try_flight_options_by_time_of_day(self):
        time_tabs = ['בוקר', 'צהריים', 'ערב']
        attempt = 1

        for label in time_tabs:
            logging.info(f"[Mobile] Trying flight time tab: {label} (Attempt {attempt})")
            try:
                self.select_time_tab(label)
                self.click_edit_departure_flight()
                self.choose_first_departure_option()

                self.click_edit_return_flight()
                self.choose_first_return_option()
                if self.ensure_passenger_form_loaded():
                    logging.info(f"[Mobile] Flight booking succeeded with tab: {label}")
                    return
            except Exception as e:
                logging.warning(f"[Mobile] Flight time tab '{label}' failed: {e}")
                attempt += 1
                continue

        logging.warning("[Mobile] All time tabs failed — moving on.")

    # Check if flight section was skipped
    def handle_passenger_form_if_flight_selection_skipped(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'פרטי הטסים')]")))
            logging.info("[Mobile] Passenger form detected, flight selection was not skipped.")
            return False
        except TimeoutException:
            logging.info("[Mobile] Flight selection was skipped — no passenger form shown.")
            return True

    # Fill + validate passenger form
    def fill_passenger_details_and_validate(self):
        try:
            logging.info("[Mobile] Filling passenger details...")
            self.wait.until(lambda d: len(
                d.find_elements(By.XPATH, "//input[@id='checkout.personal_details_form.label_first_name']")) >= 4)

            names = ["יוסי", "נועה", "דוד", "תינוק"]
            birthdates = ["01/01/2015", "01/01/2024"]

            for i in range(4):
                # First Name
                fn = self.driver.find_element(By.XPATH,
                                              f"(//input[@id='checkout.personal_details_form.label_first_name'])[{i + 1}]")
                self.scroll_and_type(fn, names[i])
                logging.info(f"First name set for passenger {i + 1}")

                # Last Name
                ln = self.driver.find_element(By.XPATH,
                                              f"(//input[@id='checkout.personal_details_form.label_last_name'])[{i + 1}]")
                self.scroll_and_type(ln, "בדיקה")

                # Birth Date (child + infant only)
                if i >= 2:
                    dob_fields = self.driver.find_elements(By.ID, "checkout.personal_details_form.label_birthDate")
                    if len(dob_fields) > (i - 2):
                        self.scroll_and_type(dob_fields[i - 2], birthdates[i - 2])
                        logging.info(f"Birthdate set for passenger {i + 1}")

            logging.info("[Mobile] Passenger form filled completely.")
        except Exception as e:
            logging.error(f"Failed to fill mobile passenger form: {e}")
            raise

    def scroll_and_type(self, element, value):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.wait.until(lambda d: element.is_displayed() and element.is_enabled())
            time.sleep(0.3)

            # Step 1: Focus & click
            self.driver.execute_script("arguments[0].focus();", element)
            element.click()

            # Step 2: Backspace clear (React-safe)
            element.clear()
            for _ in range(20):
                element.send_keys("\ue003")  # BACKSPACE
                time.sleep(0.03)

            # Step 3: Type char-by-char
            for char in value:
                element.send_keys(char)
                time.sleep(0.04)

            # Step 4: Trigger blur to confirm value
            self.driver.execute_script("arguments[0].blur();", element)

            # Step 5: Log actual value
            actual_val = self.driver.execute_script("return arguments[0].value;", element)
            logging.info(f"Set value: '{actual_val}' for element ID='{element.get_attribute('id')}'")

        except ElementNotInteractableException:
            logging.warning("Element not interactable. Using ActionChains fallback.")
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).click().pause(0.3)
                for char in value:
                    actions.send_keys(char).pause(0.05)
                actions.perform()
                logging.info("Typed value with ActionChains.")
            except Exception as e:
                logging.error(f"ActionChains fallback failed: {e}")
                raise

        except Exception as e:
            logging.error(f"Failed to type into element: {e}")
            raise

    def click_edit_departure_flight(self):
        try:
            logging.info("[Mobile] Clicking 'עריכה' for departure flight")
            departure_edit_btn = self.wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//span[contains(text(),'טיסת הלוך')]/ancestor::div[contains(@class,'sc-5602081d-1')]//span[text()='עריכה']"
            )))
            self.driver.execute_script("arguments[0].click();", departure_edit_btn)
            logging.info("'עריכה' clicked for departure flight")
        except Exception as e:
            logging.error(f"Failed to click departure edit button: {e}")
            raise

    def choose_first_departure_option(self):
        try:
            logging.info("Selecting first mobile departure option")
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'שינוי טיסת הלוך')]")))
            radios = self.driver.find_elements(By.XPATH,
                                               "//span[contains(text(),'שינוי טיסת הלוך')]/ancestor::div[contains(@class,'sc-a5db3e2f-0')]//input[@type='radio']")
            if radios:
                self.driver.execute_script("arguments[0].click();", radios[0])
                logging.info("Clicked departure radio button via JS.")
            else:
                raise Exception("No departure radio buttons found.")
        except Exception as e:
            logging.error(f"Failed to select mobile departure flight: {e}")
            raise

    def click_edit_return_flight(self):
        try:
            logging.info("[Mobile] Clicking 'עריכה' for return flight")
            return_edit_btn = self.wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//span[contains(text(),'טיסת חזור')]/ancestor::div[contains(@class,'sc-5602081d-1')]//span[text()='עריכה']"
            )))
            self.driver.execute_script("arguments[0].click();", return_edit_btn)
            logging.info("'עריכה' clicked for return flight")
        except Exception as e:
            logging.error(f"Failed to click return edit button: {e}")
            raise

    def choose_first_return_option(self):
        try:
            logging.info("Selecting first mobile return option")
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'שינוי טיסת חזור')]")))
            radios = self.driver.find_elements(By.XPATH,
                                               "//span[contains(text(),'שינוי טיסת חזור')]/ancestor::div[contains(@class,'sc-a5db3e2f-0')]//input[@type='radio']")
            if len(radios) >= 1:
                self.driver.execute_script("arguments[0].click();", radios[0])
                logging.info("Clicked return radio button via JS.")
            else:
                raise Exception("No return radio buttons found.")
        except Exception as e:
            logging.error(f"Failed to select mobile return flight: {e}")
            raise

    def confirm_flight_selection(self):
        try:
            logging.info("Confirming flight selection (Mobile)")
            confirm_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'המשך')]"))
            )
            confirm_btn.click()
            logging.info("Confirm button clicked")
        except Exception as e:
            logging.error(f"Failed to click confirm: {e}")
            raise

    def ensure_passenger_form_loaded(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'פרטי הטסים')]")))
            return True
        except TimeoutException:
            return False

    def fill_adult_passenger_details(self):
        try:
            logging.info("[Mobile] Filling details for 2 adult passengers...")

            # Wait until both adult passenger containers are visible
            adult_containers = self.wait.until(lambda d: d.find_elements(
                By.CSS_SELECTOR, "div[id^='checkout-passenger-details-row_adult_']"))

            if len(adult_containers) < 2:
                raise Exception("Less than 2 adult passenger containers found.")

            first_names = ["Daniel", "Chen"]
            last_name = "Test"

            for i, container in enumerate(adult_containers[:2]):
                logging.info(f"Filling form for adult #{i + 1}...")

                # First Name
                first_name_input = container.find_element(
                    By.CSS_SELECTOR, "input[id^='checkout-form-field-input_adult_']")
                self.type_into_react_field(first_name_input, first_names[i], label=f"First Name {i + 1}")

                # Last Name
                last_name_input = container.find_elements(
                    By.CSS_SELECTOR, "input[id^='checkout-form-field-input_adult_']")[1]
                self.type_into_react_field(last_name_input, last_name, label=f"Last Name {i + 1}")

            logging.info("[Mobile] Adult passenger form fields filled.")

        except Exception as e:
            logging.error(f"Failed to fill adult passenger form: {e}")
            self.driver.save_screenshot("error_fill_adults.png")
            raise

    def type_into_react_field(self, element, text, label="field"):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.driver.execute_script("arguments[0].focus();", element)
            time.sleep(0.2)

            element.click()
            element.clear()

            for _ in range(20):
                element.send_keys("\ue003")
                time.sleep(0.01)

            # Attempt typing normally
            element.send_keys(text)
            logging.info(f"Typed normally into '{label}'")

        except ElementNotInteractableException:
            logging.warning(f"Element not interactable: '{label}'. Using JS React fallback.")

            try:
                set_value_script = """
                var el = arguments[0];
                var value = arguments[1];
                var lastValue = el.value;
                el.value = value;
                var event = new Event('input', { bubbles: true });
                event.simulated = true;
                var tracker = el._valueTracker;
                if (tracker) {
                    tracker.setValue(lastValue);
                }
                el.dispatchEvent(event);
                el.dispatchEvent(new Event('change', { bubbles: true }));
                """
                self.driver.execute_script(set_value_script, element, text)
                logging.info(f"JS React fallback succeeded for '{label}'")

            except Exception as js_error:
                logging.error(f"JS fallback failed for '{label}': {js_error}")
                raise

        except Exception as e:
            logging.error(f"Unexpected error in '{label}': {e}")
            raise

    def select_time_tab(self, label):
        try:
            logging.info(f"[Mobile] Clicking time tab '{label}'...")

            # Try more flexible XPath — button or div/span
            tab_xpath = f"//*[self::button or self::div or self::span][contains(text(),'{label}')]"

            # Wait until at least one matching element is present
            self.wait.until(EC.presence_of_element_located((By.XPATH, tab_xpath)))
            elements = self.driver.find_elements(By.XPATH, tab_xpath)

            for el in elements:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    time.sleep(0.3)
                    self.driver.execute_script("arguments[0].click();", el)
                    logging.info(f"Clicked time tab: {label}")
                    return
                except Exception as click_error:
                    logging.warning(f"Could not click element with label '{label}' — trying next...")

            raise Exception(f"No clickable tab found for '{label}'")

        except Exception as e:
            logging.error(f"Failed to click time tab '{label}': {e}")
            raise

    def click_continue_button(self):
        try:
            logging.info("Looking for 'המשך' continue button by ID 'checkout-flights-button-submit'...")

            btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "checkout-flights-button-submit"))
            )

            # Scroll to make sure it's in view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(0.5)  # give UI time to settle

            try:
                # Native click attempt
                btn.click()
            except ElementClickInterceptedException:
                logging.warning("Click was intercepted — falling back to JS click.")
                self.driver.execute_script("arguments[0].click();", btn)

            logging.info("Clicked 'המשך' continue button successfully.")

        except Exception as e:
            logging.error(f"Failed to click continue button: {e}")
            self.driver.save_screenshot("screenshot_continue_button_fail.png")
            raise


