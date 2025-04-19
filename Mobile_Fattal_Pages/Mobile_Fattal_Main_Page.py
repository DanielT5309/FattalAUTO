from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import random
import logging
from datetime import datetime
import os
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)


class FattalMainPageMobile:
    def __init__(self, driver: webdriver.Chrome):
        self.wait = WebDriverWait(driver, 10)
        self.driver = driver

    def click_mobile_hotel_search_input(self):
        try:
            search_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sc-187e5bb0-1.clSVVm"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_box)
            self.driver.execute_script("arguments[0].click();", search_box)
            logging.info("Clicked mobile hotel search input container.")
        except Exception as e:
            logging.error(f"Failed to click mobile hotel search input: {e}")
            self.take_screenshot("click_mobile_hotel_search_input_fail")
            raise

    def set_city_mobile(self, city_name: str):
        try:
            input_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "main-input"))
            )
            input_field.clear()
            input_field.send_keys(city_name)
            input_field.click()
            logging.info(f"Typed city name in mobile: {city_name}")
        except Exception as e:
            logging.error(f"Failed to set city on mobile: {e}")


    def take_screenshot(self, name="error_screenshot"):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_dir = os.path.join(os.getcwd(), "Screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        path = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(path)
        logging.error(f"Screenshot saved: {path}")

    def click_first_suggested_hotel(self):
        try:
            suggestion_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "search-engine-input-rendered-hotel-item"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", suggestion_btn)
            suggestion_btn.click()
            logging.info("Clicked first suggested hotel from list.")
        except Exception as e:
            logging.error(f"Failed to click first suggested hotel: {e}")
            self.take_screenshot("click_suggested_hotel_fail")
            raise

    def click_mobile_date_picker(self):
        try:
            date_picker = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "search-engine-date-picker-month-button"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_picker)
            date_picker.click()
            logging.info("Opened mobile calendar (date picker).")
        except Exception as e:
            logging.error(f"Failed to open date picker: {e}")
            self.take_screenshot("open_calendar_fail")
            raise

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    import time
    import random
    import logging

    def select_date_range_two_months_ahead(self, stay_length=None):
        """
        Selects check-in and check-out dates from the 3rd calendar month shown (2 months ahead).
        :param stay_length: Optional integer for number of nights. If None, chooses randomly (3-5).
        """
        try:
            logging.info("Scrolling and selecting date range (real clicks)...")

            months = self.driver.find_elements(By.ID, "search-engine-date-picker-mobile-month-wrapper")
            if len(months) < 3:
                raise Exception("Less than 3 months available in calendar")

            target_month = months[2]
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_month)
            time.sleep(2)

            valid_buttons = target_month.find_elements(By.XPATH, ".//button[not(@disabled)]")
            if len(valid_buttons) < 8:
                raise Exception("Not enough active date buttons in target month")

            # ✅ Use passed value or randomize
            stay_length = stay_length or random.randint(3, 5)
            start_idx = random.randint(0, len(valid_buttons) - stay_length - 1)
            checkin = valid_buttons[start_idx]
            checkout = valid_buttons[start_idx + stay_length]

            checkin_label = checkin.find_element(By.TAG_NAME, "abbr").get_attribute("aria-label")
            checkout_label = checkout.find_element(By.TAG_NAME, "abbr").get_attribute("aria-label")
            logging.info(f"Attempting to select: {checkin_label} to {checkout_label} ({stay_length} לילות)")

            actions = ActionChains(self.driver)
            actions.move_to_element(checkin).pause(0.5).click().pause(1.0)
            actions.move_to_element(checkout).pause(0.5).click().perform()

            try:
                self.driver.find_element(By.ID, "search-engine-date-picker-mobile-month-wrapper")
                logging.info("Calendar still open after selection – continuing.")
            except:
                raise Exception("Calendar closed before both dates were selected!")

            continue_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'sc-f6382f5-0') and contains(text(), 'המשך')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
            time.sleep(0.4)
            continue_btn.click()

            logging.info(f"Selected check-in: {checkin_label} → check-out: {checkout_label}")
            logging.info("Confirmed calendar selection.")

        except Exception as e:
            logging.error(f"Date selection failed: {e}")
            self.take_screenshot("calendar_selection_fail")
            raise

    def get_valid_calendar_day_buttons(self):
        buttons = self.driver.find_elements(By.CSS_SELECTOR, ".react-calendar__month-view__days button")
        return [
            btn for btn in buttons
            if btn.is_enabled() and "neighboringMonth" not in btn.get_attribute("class")
        ]

    def click_mobile_room_selection(self):
        try:
            # Check if the modal is already open
            modal_open = False
            try:
                WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.ID, "search-engine-build-room-mobile-wrapper-adults0"))
                )
                modal_open = True
                logging.info("Room modal already open — skip clicking.")
            except TimeoutException:
                modal_open = False

            if not modal_open:
                room_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "search-engine-room-selection-button-Main"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", room_button)
                self.driver.execute_script("arguments[0].click();", room_button)
                logging.info("Clicked to open mobile room selection modal.")
            else:
                logging.info("Room modal already open — did not click again.")

        except Exception as e:
            logging.error(f"Failed to trigger room modal: {e}")
            self.take_screenshot("open_room_modal_fail")
            raise

    # ⬇️ Make sure this is NOT indented under the previous method
    def set_mobile_room_occupants(self, adults=2, children=0, infants=0):
        """Adjust room occupants assuming the modal is already open. Does NOT open modal or click 'המשך'."""
        try:
            logging.info("Adjusting room occupants...")

            # Map of room sections
            room_config = {
                "adults": adults,
                "children": children,
                "infants": infants
            }

            # Wait until the modal structure is present
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "search-engine-build-room-mobile-room-container0"))
            )
            logging.info("Room modal confirmed present.")

            for section, desired in room_config.items():
                logging.info(f"Setting {section} to {desired}...")

                count_id = f"search-engine-build-room-mobile-count-{section}0"
                plus_id = f"search-engine-build-room-mobile-wrapper-{section}0"
                minus_id = f"search-engine-build-room-mobile-wrapper-{section}-remove0"

                # Wait for count element to show up and get initial value
                count_el = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, count_id))
                )
                plus_btn = self.driver.find_element(By.ID, plus_id)
                minus_btn = self.driver.find_element(By.ID, minus_id)

                current = int(self.driver.execute_script("return arguments[0].textContent.trim();", count_el))

                # Increase or decrease until we reach desired
                while current < desired:
                    self.driver.execute_script("arguments[0].click();", plus_btn)
                    current += 1
                    time.sleep(0.25)

                while current > desired:
                    if minus_btn.get_attribute("disabled"):
                        logging.warning(f"Cannot reduce {section} below {current}. Button disabled.")
                        break
                    self.driver.execute_script("arguments[0].click();", minus_btn)
                    current -= 1
                    time.sleep(0.25)

                logging.info(f"{section.capitalize()} set to: {current}")

            logging.info("Room occupant adjustment completed.")

        except Exception as e:
            logging.error(f"Failed during occupant setting: {e}")
            self.take_screenshot("room_occupants_adjustment_fail")
            raise

    def click_continue_room_button_mobile(self):
        """Clicks the 'Continue - חדר' button after selecting room occupants."""
        self.click_room_continue_button()

    def click_mobile_search_button(self):
        logging.info("Attempting to click main 'חפש חופשה' search button...")

        try:
            # Step 1: Ensure modal is closed
            try:
                WebDriverWait(self.driver, 5).until_not(
                    EC.presence_of_element_located((By.ID, "search-engine-build-room-mobile-wrapper-adults0"))
                )
                logging.info("Room modal is now fully closed.")
            except TimeoutException:
                logging.warning("Room modal may still be open — click might be blocked.")

            # Step 2: Re-fetch the search button
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search-engine-search-button-mobile-button-main"))
            )
            search_btn = self.driver.find_element(By.ID, "search-engine-search-button-mobile-button-main")

            # Step 3: Confirm text is correct
            btn_text = self.driver.execute_script("return arguments[0].textContent.trim();", search_btn)
            logging.info(f"Found button with text: '{btn_text}'")
            if "חפש" not in btn_text:
                raise Exception("Search button text does not contain 'חפש'.")

            # Step 4: Scroll & confirm it's clickable
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_btn)
            time.sleep(0.4)

            # Step 5: Confirm it's NOT blocked by another element
            self.driver.execute_script("""
                const btn = arguments[0];
                const rect = btn.getBoundingClientRect();
                const topElement = document.elementFromPoint(rect.left + 10, rect.top + 10);
                if (topElement !== btn) throw new Error('Search button is visually blocked.');
            """, search_btn)

            # Step 6: Click via JS
            self.driver.execute_script("arguments[0].click();", search_btn)
            logging.info("Clicked search button (JS click).")


        except Exception as e:
            self.take_screenshot("search_button_click_fail")
            logging.error(f"Failed to click 'חפש חופשה': {e}")
            raise

    def close_room_modal_mobile(self):
        """
        Clicks the הרכב button again to close the mobile room modal.
        """
        try:
            room_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "search-engine-room-selection-button-Main"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", room_button)
            self.driver.execute_script("arguments[0].click();", room_button)
            logging.info("Closed room modal by re-clicking הרכב.")
        except Exception as e:
            logging.error(f"Failed to close room modal: {e}")
            self.take_screenshot("close_room_modal_fail")
            raise

    def reopen_and_close_calendar_after_room_set(self):
        """Clicks the calendar (תאריכים) button once after room selection to reset any lingering focus."""
        try:
            logging.info("Clicking תאריכים to force close modals before final search...")

            calendar_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "search-engine-date-picker-month-button"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", calendar_btn)
            self.driver.execute_script("arguments[0].click();", calendar_btn)
            time.sleep(0.6)  # Let the UI catch up

            # Just click it once — no date selection needed
            logging.info("Re-clicked calendar (תאריכים) to close if open.")

        except Exception as e:
            logging.error(f"Failed to re-click calendar after room selection: {e}")
            self.take_screenshot("reclick_calendar_fail")
            raise

    def select_flight_option_all_airports(self):
        try:
            logging.info("Opening flight dropdown and selecting 'מכל שדות התעופה'...")

            dropdown_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "search-engine-search-field-button_flights"))
            )

            # Safe scroll + JS click to avoid interception
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_btn)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", dropdown_btn)

            all_flights_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "search-engine-flight-select-option_all_flights"))
            )
            time.sleep(0.2)
            self.driver.execute_script("arguments[0].click();", all_flights_btn)

            logging.info("Selected 'מכל שדות התעופה' for flights.")

        except Exception as e:
            self.take_screenshot("flight_select_fail")
            logging.error(f"Failed to select flight option 'מכל שדות התעופה': {e}")
            raise

    def click_first_suggested_region(self):
        try:
            suggestion_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "search-engine-input-rendered-item"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", suggestion_btn)
            suggestion_btn.click()
            logging.info("Clicked first suggested region from list.")
        except Exception as e:
            logging.error(f"Failed to click first suggested region: {e}")
            self.take_screenshot("click_suggested_region_fail")
            raise

    def select_specific_date_range(self, checkin_day, checkout_day):
        try:
            logging.info(f"Selecting specific range: {checkin_day} to {checkout_day}")

            months = self.driver.find_elements(By.ID, "search-engine-date-picker-mobile-month-wrapper")
            if len(months) < 2:
                raise Exception("Not enough months rendered in calendar.")

            # We'll loop through both available months to find our buttons
            checkin_btn = None
            checkout_btn = None

            for month in months:
                buttons = month.find_elements(By.XPATH, ".//button[not(@disabled)]")

                for btn in buttons:
                    try:
                        label = btn.find_element(By.TAG_NAME, "abbr").get_attribute("aria-label")
                        if f"{checkin_day} בספטמבר" in label:
                            checkin_btn = btn
                        if f"{checkout_day} בספטמבר" in label:
                            checkout_btn = btn
                    except Exception:
                        continue

            if not checkin_btn or not checkout_btn:
                raise Exception(f"Could not find one or both dates: {checkin_day}, {checkout_day}")

            # Scroll and click
            actions = ActionChains(self.driver)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkin_btn)
            actions.move_to_element(checkin_btn).pause(0.5).click().pause(1.0)

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkout_btn)
            actions.move_to_element(checkout_btn).pause(0.5).click().perform()

            logging.info(f"Clicked check-in: {checkin_day} ביוני")
            logging.info(f"Clicked check-out: {checkout_day} ביוני")

            continue_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'sc-f6382f5-0') and contains(text(), 'המשך')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
            time.sleep(0.4)
            continue_btn.click()

            logging.info("Confirmed calendar selection.")

        except Exception as e:
            self.take_screenshot("select_specific_date_range_fail")
            logging.error(f"Failed selecting specific date range: {e}")
            raise

    def click_room_continue_button(self):
        logging.info("Searching for 'המשך' room continue button...")

        try:
            # Wait until modal is still visible
            if not self.wait_for_room_modal_open(timeout=3):
                raise TimeoutException("Room modal is not visible.")

            xpath = "//div[contains(@class, 'sc-f6382f5-0') and contains(text(), 'המשך')]"

            continue_btn = WebDriverWait(self.driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
            time.sleep(0.3)

            try:
                continue_btn.click()
                logging.info("Clicked room continue button (native click).")
            except Exception:
                self.driver.execute_script("arguments[0].click();", continue_btn)
                logging.info("Clicked room continue button (JS fallback).")

        except Exception as e:
            self.take_screenshot("room_continue_click_fail")
            logging.error(f"Could not click 'המשך' continue button: {e}")
            raise TimeoutException("'המשך' button not found or not clickable.")

    def wait_for_room_modal_open(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "search-engine-build-room-mobile-wrapper-adults0"))
            )
            logging.info("Room modal is visible and ready.")
            return True
        except TimeoutException:
            logging.warning("Room modal is NOT visible!")
            return False

    def open_promo_code_input(self):
        """Clicks the 'יש לי קוד ארגון' button to reveal the promo code input field."""
        try:
            open_button = self.driver.find_element(By.ID, "search-engine-promo-code-closed-root")
            open_button.click()
            logging.info("Clicked 'יש לי קוד ארגון' to reveal promo input.")
        except Exception as e:
            logging.warning(f"Failed to click promo code opener: {e}")

    def enter_promo_code(self, promo_code: str):
        """Inputs the promo code and triggers validation by clicking outside the input field."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "search-engine-promo-code-input"))
            )
            promo_input = self.driver.find_element(By.ID, "search-engine-promo-code-input")
            promo_input.clear()
            promo_input.send_keys(promo_code)
            logging.info(f"Promo code '{promo_code}' entered successfully.")

            # Click outside to trigger blur (we'll click the body or header)
            self.driver.find_element(By.TAG_NAME, "body").click()
            logging.info("Clicked outside to close promo input.")

        except Exception as e:
            logging.error(f"Failed to enter promo code: {e}")

    def is_promo_code_applied(self, expected_code: str = "FHVR") -> bool:
        """
        Verifies that the promo code input field contains the expected value.
        """
        try:
            input_field = self.driver.find_element(By.ID, "search-engine-promo-code-input")
            actual_value = input_field.get_attribute("value")
            logging.info(f"Promo input contains: {actual_value}")
            return actual_value.strip().upper() == expected_code.upper()
        except Exception as e:
            logging.warning(f"Could not verify promo code input: {e}")
            return False



















