from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
import random
import logging
from datetime import datetime
import os
# Set up logging configuration once
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)


class FattalMainPage:
        def __init__(self, driver: webdriver.Chrome):
            self.wait = WebDriverWait(driver, 10)
            self.driver = driver

        def deal_popup(self):
            try:
                close_button = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "ex-popup-modal-close-btn"))
                )
                self.driver.execute_script("arguments[0].click();", close_button)
                logging.info("Popup closed.")
            except:
                logging.info("Popup not found — continuing without closing.")

        def click_clear_button_hotel(self):
            try:
                clear_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='נקה שדה']"))
                )
                clear_button.click()
                logging.info("Cleared hotel input field.")
            except Exception as e:
                logging.warning(f"Failed to clear hotel input field: {e}")

        def select_flight_option_all_airports(self):
            try:
                # Step 1: Open flight filter section (if applicable)
                try:
                    dropdown_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "search-engine-flight-select-option_all_flights"))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_btn)
                    dropdown_btn.click()
                    logging.info("Selected flight option: מכל שדות התעופה")
                except Exception as e:
                    logging.warning(f"Primary flight button by ID not clickable: {e}")
                    raise

            except Exception as e:
                logging.error(f"Failed to select flight option: {e}")
                raise

        def trigger_suggestions(self):
            try:
                input_field = self.driver.find_element(By.ID, "main-input")
                input_field.click()
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[text()='יעדים שעשויים לעניין אותך']"))
                )
                logging.info("Suggestions triggered.")
            except Exception as e:
                logging.warning(f"Failed to trigger suggestions: {e}")

        # Type a city name in the input field
        def type_city_name(self, city_name: str):
            try:
                input_field = self.driver.find_element(By.ID, "main-input")
                input_field.clear()
                input_field.send_keys(city_name)
                input_field.click()
                logging.info(f"Typed city name: {city_name}")
            except Exception as e:
                logging.warning(f"Failed to type city name '{city_name}': {e}")

        # Click a suggestion button (from the autocomplete menu)
        def click_suggestion_button(self, button):
            try:
                chosen_text = button.text
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(button))
                self.driver.execute_script("arguments[0].click();", button)
                logging.info(f"נבחרה הצעה: {chosen_text}")
            except Exception as e:
                logging.warning(f"Failed to click suggestion button: {e}")

        # Wait for suggestion buttons to appear
        def wait_for_suggestion_container(self):
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-c017a840-10.dBYtDd button"))
                )
                logging.info("Suggestion container is visible.")
            except Exception as e:
                logging.warning(f"Suggestion container not found: {e}")

        # Find the suggestion button containing specific city name
        def find_suggestion_button(self, city_name: str):
            try:
                buttons = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.sc-c017a840-10.dBYtDd button"))
                )
                for btn in buttons:
                    if city_name in btn.text:
                        logging.info(f"Suggestion button found for city: {city_name}")
                        return btn
                logging.warning(f"No suggestion button matched city: {city_name}")
                return None
            except Exception as e:
                logging.warning(f"Error finding suggestion buttons: {e}")
                return None

        # Set the city from the suggestions popup using JS click
        def set_city(self, city_name: str):
            self.type_city_name(city_name)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.autocomplete-menu button"))
                )
                time.sleep(1.2)

                first_suggestion = self.driver.execute_script("""
                    const suggestions = document.querySelectorAll("div.autocomplete-menu button");
                    if (suggestions.length > 0) {
                        suggestions[0].scrollIntoView({block: "center"});
                        suggestions[0].click();
                        return suggestions[0].innerText;
                    }
                    return null;
                """)

                if first_suggestion:
                    logging.info(f"נבחרה ההצעה הראשונה: {first_suggestion.strip()}")
                else:
                    raise Exception("No suggestions rendered")
            except Exception as e:
                logging.error(f"JavaScript click failed for city '{city_name}': {e}")
                raise
        # Open calendar widget
        def open_calendar(self):
            try:
                # Wait for the calendar toggle button to become clickable
                calendar_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "search-engine-date-picker-display-container-2"))
                )

                try:
                    calendar_btn.click()
                    logging.info("Clicked calendar button using ID.")
                except Exception as click_error:
                    logging.warning(f"Normal click failed: {click_error} — trying JS fallback.")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", calendar_btn)
                    self.driver.execute_script("arguments[0].click();", calendar_btn)
                    logging.info("Clicked calendar button using JS fallback.")

                # Wait for the calendar container or the day grid to appear
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "search-engine-date-picker-container"))
                )
                logging.info("Calendar is now visible and ready for selection.")

            except Exception as e:
                logging.error(f"Failed to open calendar: {e}")
                raise

        # Switch to the arrival tab in the calendar (if not already active)
        def switch_to_arrival_tab(self):
            try:
                arrival_tab = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//div[text()='בחירת תאריך הגעה']"))
                )
                arrival_tab.click()
            except:
                logging.info("Arrival date wasn't chosen")

        # Get valid (enabled) calendar day buttons
        def get_valid_date_buttons(self):
            try:
                buttons = self.driver.find_elements(By.XPATH,
                                                    "//button[contains(@class, 'react-calendar__tile') and not(@disabled)]")
                return buttons
            except Exception as e:
                logging.error(f"Failed getting valid date buttons: {e}")
                return []

        def select_single_day_next_month(self):
            logging.info("Selecting a single day in next month")
            try:
                self.open_calendar()
                self.switch_to_arrival_tab()

                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'react-calendar__navigation__next-button')]"))
                )
                try:
                    next_button.click()
                    logging.info("Clicked next month.")
                except Exception as e:
                    logging.warning(f"Normal click failed: {e} — trying JS fallback.")
                    self.driver.execute_script("arguments[0].click();", next_button)

                time.sleep(1)
                valid_dates = self.get_valid_date_buttons()
                if not valid_dates:
                    raise Exception("No valid days found to select.")

                selected_day = random.choice(valid_dates)
                selected_day_text = selected_day.text
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_day)
                self.driver.execute_script("arguments[0].click();", selected_day)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", selected_day)
                # Close calendar (ESCAPE)
                body = self.driver.find_element(By.TAG_NAME, 'body')
                body.send_keys(Keys.ESCAPE)
                time.sleep(1)  # Give the browser a moment to react

                # ✅ Wait until the calendar modal disappears before moving on
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "react-calendar"))
                )

                logging.info("Calendar closed successfully — ready to select room occupants.")

                logging.info(f"Selected same check-in/out day: {selected_day_text}")
            except Exception as e:
                logging.error(f"Failed to select single day: {e}")
                raise

        def select_random_date_range_two_months_ahead(self, min_nights: int = 3, max_nights: int = 5) -> None:
            try:
                logging.info("Starting 2 months ahead date range selection (with double click method)")

                self.open_calendar()
                self.switch_to_arrival_tab()

                # Move 2 months ahead
                for _ in range(2):
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(@class, 'react-calendar__navigation__next-button')]"))
                    )
                    try:
                        next_button.click()
                        logging.info("Clicked next month.")
                    except Exception as click_err:
                        logging.warning(f"Normal click failed: {click_err}. Trying JS fallback...")
                        self.driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(1)

                # Find valid dates
                valid_dates = self.get_valid_date_buttons()
                if not valid_dates or len(valid_dates) < min_nights:
                    raise Exception("Not enough valid dates to select range.")

                # Random pick
                max_start_index = len(valid_dates) - min_nights
                start_index = random.randint(0, max_start_index)
                nights = random.randint(min_nights, max_nights)
                end_index = start_index + nights
                if end_index >= len(valid_dates):
                    end_index = len(valid_dates) - 1

                check_in = valid_dates[start_index]
                check_in_text = check_in.text
                check_out = valid_dates[end_index]
                check_out_text = check_out.text

                actions = ActionChains(self.driver)

                # 1️⃣ Click End Date first (this clears previous selection!)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", check_out)
                actions.move_to_element(check_out).pause(0.2).click().perform()
                time.sleep(0.5)

                # 2️⃣ Click Start Date
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", check_in)
                actions.move_to_element(check_in).pause(0.2).click().perform()
                time.sleep(0.5)

                # 3️⃣ Click End Date Again
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", check_out)
                actions.move_to_element(check_out).pause(0.2).click().perform()

                logging.info(f"Selected custom stay: {check_in_text} to {check_out_text} ({nights} nights)")

                # Close the calendar
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(1)  # Give browser a moment to react

                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "react-calendar"))
                )

                logging.info("Calendar closed successfully — ready to select room occupants.")

            except Exception as e:
                logging.error(f"Failed selecting 2 months ahead with corrected double-click logic: {e}")
                self.take_screenshot("calendar_selection_fail")
                raise

        def select_next_month_date_range(self, min_nights: int =3, max_nights: int = 4) -> None:
            try:
                logging.info("Starting 2 months ahead date range selection (3-5 nights)")

                # Open calendar
                self.open_calendar()
                self.switch_to_arrival_tab()

                # Move 2 months forward
                for _ in range(2):
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(@class, 'react-calendar__navigation__next-button')]"))
                    )
                    try:
                        next_button.click()
                        logging.info("Clicked next month.")
                    except Exception as click_err:
                        logging.warning(f"Normal click failed: {click_err}. Trying JS fallback...")
                        self.driver.execute_script("arguments[0].click();", next_button)
                        logging.info("Clicked next month via JS fallback.")
                    time.sleep(0.5)

                # Find available dates
                valid_dates = self.get_valid_date_buttons()
                if not valid_dates or len(valid_dates) < min_nights:
                    raise Exception("Not enough valid dates found to select range.")

                # Random pick start date
                max_start_index = len(valid_dates) - min_nights
                start_index = random.randint(0, max_start_index)
                nights = random.randint(min_nights, max_nights)
                end_index = start_index + nights

                if end_index >= len(valid_dates):
                    end_index = len(valid_dates) - 1

                check_in_element = valid_dates[start_index]
                check_out_element = valid_dates[end_index]

                check_in_text = check_in_element.get_attribute("aria-label") or check_in_element.text
                check_out_text = check_out_element.get_attribute("aria-label") or check_out_element.text

                # Click check-in
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", check_in_element)
                ActionChains(self.driver).move_to_element(check_in_element).pause(0.2).click().perform()
                time.sleep(0.5)

                # Click check-out
                valid_dates_after_checkin = self.get_valid_date_buttons()
                if end_index >= len(valid_dates_after_checkin):
                    end_index = len(valid_dates_after_checkin) - 1
                check_out_element = valid_dates_after_checkin[end_index]

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", check_out_element)
                ActionChains(self.driver).move_to_element(check_out_element).pause(0.2).click().perform()
                time.sleep(0.5)

                # ✅ Try clicking the "המשך" (continue) button if exists
                try:
                    continue_date_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "search-engine-date-picker-footer-side-button"))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_date_button)
                    continue_date_button.click()
                    logging.info("Clicked 'Continue' button after selecting dates.")
                except TimeoutException:
                    logging.info("No 'Continue' button found after selecting dates. Skipping.")
                except Exception as e:
                    logging.warning(f"Error clicking 'Continue' after dates: {e}")

                # Save selections to instance for logging later 📋
                self.selected_checkin_date = check_in_text
                self.selected_checkout_date = check_out_text
                self.selected_nights = nights

                logging.info(
                    f"✅ Selected stay: Check-in: {self.selected_checkin_date}, Check-out: {self.selected_checkout_date}, Nights: {self.selected_nights}"
                )

            except Exception as e:
                logging.error(f"Failed selecting date range 2 months ahead: {e}")
                self.take_screenshot("calendar_selection_fail")
                raise

        def set_room_occupants(self, adults=2, children=0, infants=0):
            try:
                logging.info("Opening room selection modal...")

                # ⚡️ Updated ID!
                button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "main-search-rooms-select"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.3)

                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "main-search-rooms-select"))
                    ).click()
                    logging.info("Clicked room selection button normally.")
                except Exception as click_error:
                    logging.warning(f"Normal click failed: {click_error}. Trying JS fallback...")
                    self.driver.execute_script("arguments[0].click();", button)
                    logging.info("Clicked room selection button via JS fallback.")

                # Wait for room selection modal to appear
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "search-engine-room-selection-popover"))
                )
                logging.info("Room selection modal is now visible.")
                time.sleep(0.5)

                # ⬇️ Inner function to select guests
                def select_guest(cell_id, value):
                    try:
                        container = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.ID, cell_id))
                        )
                        dropdown_button = container.find_element(By.TAG_NAME, "button")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_button)
                        dropdown_button.click()
                        logging.info(f"Opened dropdown for {cell_id}.")
                        time.sleep(0.3)

                        options = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[id^='select-options_'] button"))
                        )

                        for option in options:
                            if option.text.strip() == str(value):
                                self.driver.execute_script("arguments[0].click();", option)
                                logging.info(f"Selected {value} for {cell_id}.")
                                break
                        else:
                            logging.warning(f"No exact match found for {value} in {cell_id}. Clicking first option.")
                            self.driver.execute_script("arguments[0].click();", options[0])

                    except Exception as e:
                        logging.error(f"Failed selecting guest for {cell_id}: {e}")
                        raise

                # 👥 Set adults, children, infants
                select_guest("search-engine-build-room-room-row-cell-adults0", adults)
                time.sleep(0.3)
                select_guest("search-engine-build-room-room-row-cell-kids0", children)
                time.sleep(0.3)
                select_guest("search-engine-build-room-room-row-cell-babies0", infants)
                time.sleep(0.3)

                # ➡️ Click continue to confirm
                continue_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "search-engine-build-room-next-button"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
                continue_btn.click()
                logging.info(f"✅ Room occupants set: {adults} adults, {children} children, {infants} infants.")

            except Exception as e:
                logging.error(f"Failed to complete room occupants selection: {e}")
                self.take_screenshot("set_room_occupants_fail")
                raise

        # Click the 'חפש' (search) button
        def search_button(self):
            try:
                result = self.driver.execute_script("""
                    const buttons = Array.from(document.querySelectorAll("button"));
                    const searchBtn = buttons.find(btn => btn.textContent.trim() === "חפש");
                    if (searchBtn) {
                        searchBtn.scrollIntoView({block: "center"});
                        searchBtn.click();
                        return searchBtn.textContent.trim();
                    }
                    return null;
                """)
                if result:
                    print(f"Search button '{result}' clicked successfully.")
                else:
                    raise Exception("Search button not found on the page")
            except Exception as e:
                print(f"Error clicking search button: {e}")
                raise

        # Get hotel link from search results by index
        def liked_hotel_links(self, hotel_index):
            return self.driver.find_elements(By.CSS_SELECTOR,
                'a.sc-b8919b5f-1.lgGiaA.sc-c2a74b5a-6.bMslGW[type="button"]'
            )[hotel_index]

        # Newsletter email field setter
        def news_letter_email_input(self, email_string):
            email = self.driver.find_element(By.CSS_SELECTOR, 'input#email')
            email.clear()
            email.send_keys(email_string)

        # Click newsletter register button
        def register_news_letter_button(self):
            self.driver.find_element(By.CSS_SELECTOR, 'button.sc-923ff82e-7.hVHcft').click()

        def close_post_login_popup(self):
            """Closes the popup/modal that appears after login."""
            try:
                popup_close_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sc-4a11a149-3.dVxqFs"))
                )
                self.driver.execute_script("arguments[0].click();", popup_close_btn)
                logging.info("Post-login popup closed.")
            except TimeoutException:
                logging.info("No post-login popup appeared — skipping.")
            except Exception as e:
                logging.warning(f"Failed to close post-login popup: {e}")
        # Footer button methods (legal, accessibility, etc.)
        # In FattalMainPage.py
        def take_screenshot(self, name="error_screenshot"):
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            screenshot_dir = os.path.join(os.getcwd(), "Screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            path = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
            self.driver.save_screenshot(path)
            logging.error(f"Screenshot saved: {path}")

        def select_specific_date_range_desktop(self, checkin_day: int, checkout_day: int, month: str = "יולי 2025"):
            try:
                logging.info(f"[DESKTOP] Selecting date range {checkin_day} to {checkout_day} in {month}")

                # Open calendar
                calendar_opener = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@id, 'date-picker')]"))
                )
                calendar_opener.click()

                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "react-calendar"))
                )

                found_checkin = False
                found_checkout = False
                attempts = 0

                while attempts < 5 and not (found_checkin and found_checkout):
                    attempts += 1
                    checkin_btn = None
                    checkout_btn = None

                    calendars = self.driver.find_elements(By.CLASS_NAME, "react-calendar__month-view")

                    for calendar in calendars:
                        buttons = calendar.find_elements(By.XPATH, ".//button[not(@disabled)]")
                        for btn in buttons:
                            try:
                                abbr = btn.find_element(By.TAG_NAME, "abbr")
                                aria_label = abbr.get_attribute("aria-label")  # Ex: "יום שבת, 6 יולי 2025"
                                if not aria_label:
                                    continue
                                parts = aria_label.split(",")[-1].strip()  # take "6 יולי 2025"
                                parts_split = parts.split(" ")

                                if len(parts_split) >= 2:
                                    day_text, month_text = parts_split[0], parts_split[1] + " " + parts_split[2]

                                    if int(day_text) == checkin_day and month_text == month:
                                        checkin_btn = btn
                                    if int(day_text) == checkout_day and month_text == month:
                                        checkout_btn = btn
                            except Exception as inner_e:
                                logging.debug(f"Skipping button due to error: {inner_e}")
                                continue

                    if checkin_btn and checkout_btn:
                        found_checkin = True
                        found_checkout = True
                        break
                    else:
                        logging.info(f"Did not find dates in attempt {attempts}. Clicking next month.")
                        next_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//button[contains(@class, 'react-calendar__navigation__next-button')]"))
                        )
                        next_btn.click()
                        time.sleep(1)

                if not found_checkin or not found_checkout:
                    raise Exception(f"Could not find the specified dates: {checkin_day} and {checkout_day} in {month}")

                # Select check-in and check-out
                actions = ActionChains(self.driver)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkin_btn)
                actions.move_to_element(checkin_btn).pause(0.5).click().pause(1.0)

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkout_btn)
                actions.move_to_element(checkout_btn).pause(0.5).click().perform()

                logging.info(f"Selected check-in {checkin_day} and check-out {checkout_day} for {month}")

                # Optional continue button
                try:
                    continue_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'המשך')]"))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
                    continue_btn.click()
                    logging.info("Clicked continue after date selection.")
                except TimeoutException:
                    logging.info("No continue button found. Skipping.")

            except Exception as e:
                self.take_screenshot("select_specific_date_range_desktop_fail")
                logging.error(f"Failed selecting date range: {e}")
                raise

        def accessibility_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(1)').click()
        def customer_support_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(2)').click()
        def terms_of_use_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(3)').click()
        def privacy_policy_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(4)').click()
        def cancel_reservation_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(5)').click()
        def fattal_hotel_group_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(6)').click()
        def accessibility_statement_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(7)').click()
        def corporate_responsibility_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(8)').click()
        def more_information_button(self): self.driver.find_element(By.CSS_SELECTOR, 'span.sc-68eae715-3.cmuwUL').click()
