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
# ✅ Set up logging configuration once
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
                logging.info("✅ Popup closed.")
            except:
                logging.info("ℹ️ Popup not found — continuing without closing.")

        def click_clear_button_hotel(self):
            try:
                clear_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='נקה שדה']"))
                )
                clear_button.click()
                logging.info("✅ Cleared hotel input field.")
            except Exception as e:
                logging.warning(f"❌ Failed to clear hotel input field: {e}")

        def select_flight_option_all_airports(self):
            try:
                # Step 1: Click the flight dropdown
                dropdown_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sc-9f775e38-1"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_btn)
                dropdown_btn.click()
                logging.info("✈️ Flight dropdown opened.")

                # Step 2: Click the desired option ("מכל שדות התעופה")
                option_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='מכל שדות התעופה']"))
                )
                self.driver.execute_script("arguments[0].click();", option_btn)
                logging.info("✅ Selected flight option: מכל שדות התעופה")

            except Exception as e:
                logging.error(f"❌ Failed to select flight option: {e}")
                raise
        def trigger_suggestions(self):
            try:
                input_field = self.driver.find_element(By.ID, "main-input")
                input_field.click()
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[text()='יעדים שעשויים לעניין אותך']"))
                )
                logging.info("✅ Suggestions triggered.")
            except Exception as e:
                logging.warning(f"❌ Failed to trigger suggestions: {e}")

        # ✅ Type a city name in the input field
        def type_city_name(self, city_name: str):
            try:
                input_field = self.driver.find_element(By.ID, "main-input")
                input_field.clear()
                input_field.send_keys(city_name)
                input_field.click()
                logging.info(f"✅ Typed city name: {city_name}")
            except Exception as e:
                logging.warning(f"❌ Failed to type city name '{city_name}': {e}")

        # ✅ Click a suggestion button (from the autocomplete menu)
        def click_suggestion_button(self, button):
            try:
                chosen_text = button.text
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(button))
                self.driver.execute_script("arguments[0].click();", button)
                logging.info(f"✅ נבחרה הצעה: {chosen_text}")
            except Exception as e:
                logging.warning(f"❌ Failed to click suggestion button: {e}")

        # ✅ Wait for suggestion buttons to appear
        def wait_for_suggestion_container(self):
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-c017a840-10.dBYtDd button"))
                )
                logging.info("✅ Suggestion container is visible.")
            except Exception as e:
                logging.warning(f"❌ Suggestion container not found: {e}")

        # ✅ Find the suggestion button containing specific city name
        def find_suggestion_button(self, city_name: str):
            try:
                buttons = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.sc-c017a840-10.dBYtDd button"))
                )
                for btn in buttons:
                    if city_name in btn.text:
                        logging.info(f"✅ Suggestion button found for city: {city_name}")
                        return btn
                logging.warning(f"❌ No suggestion button matched city: {city_name}")
                return None
            except Exception as e:
                logging.warning(f"❌ Error finding suggestion buttons: {e}")
                return None

        # ✅ Set the city from the suggestions popup using JS click
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
                    logging.info(f"✅ נבחרה ההצעה הראשונה: {first_suggestion.strip()}")
                else:
                    raise Exception("No suggestions rendered")
            except Exception as e:
                logging.error(f"❌ JavaScript click failed for city '{city_name}': {e}")
                raise
        # ✅ Open calendar widget
        def open_calendar(self):
            try:
                # Wait for the calendar toggle button to become clickable
                calendar_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "search-engine-date-picker-display-container-2"))
                )

                try:
                    calendar_btn.click()
                    logging.info("✅ Clicked calendar button using ID.")
                except Exception as click_error:
                    logging.warning(f"⚠️ Normal click failed: {click_error} — trying JS fallback.")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", calendar_btn)
                    self.driver.execute_script("arguments[0].click();", calendar_btn)
                    logging.info("✅ Clicked calendar button using JS fallback.")

                # Wait for the calendar container or the day grid to appear
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "search-engine-date-picker-container"))
                )
                logging.info("✅ Calendar is now visible and ready for selection.")

            except Exception as e:
                logging.error(f"❌ Failed to open calendar: {e}")
                raise

        # ✅ Switch to the arrival tab in the calendar (if not already active)
        def switch_to_arrival_tab(self):
            try:
                arrival_tab = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//div[text()='בחירת תאריך הגעה']"))
                )
                arrival_tab.click()
            except:
                logging.info("ℹ️ Arrival date wasn't chosen")

        # ✅ Get valid (enabled) calendar day buttons
        def get_valid_date_buttons(self):
            buttons = self.driver.find_elements(By.CSS_SELECTOR, ".react-calendar__month-view__days button")
            return [
                btn for btn in buttons
                if btn.is_enabled() and "react-calendar__month-view__days__day--neighboringMonth" not in btn.get_attribute(
                    "class")
            ]

        def select_single_day_next_month(self):
            logging.info("📅 Selecting a single day in next month")
            try:
                self.open_calendar()
                self.switch_to_arrival_tab()

                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'react-calendar__navigation__next-button')]"))
                )
                try:
                    next_button.click()
                    logging.info("✅ Clicked next month.")
                except Exception as e:
                    logging.warning(f"⚠️ Normal click failed: {e} — trying JS fallback.")
                    self.driver.execute_script("arguments[0].click();", next_button)

                time.sleep(1)
                valid_dates = self.get_valid_date_buttons()
                if not valid_dates:
                    raise Exception("❌ No valid days found to select.")

                selected_day = random.choice(valid_dates)
                selected_day_text = selected_day.text
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_day)
                self.driver.execute_script("arguments[0].click();", selected_day)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", selected_day)
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                logging.info(f"✅ Selected same check-in/out day: {selected_day_text}")
            except Exception as e:
                logging.error(f"❌ Failed to select single day: {e}")
                raise

        def select_next_month_date_range(self) -> None:
            try:
                self.open_calendar()
                self.switch_to_arrival_tab()

                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(@class, 'react-calendar__navigation__next-button')]"))
                    )
                    try:
                        next_button.click()
                        logging.info("✅ Clicked next month.")
                    except Exception as click_err:
                        logging.warning(f"⚠️ Normal next button click failed: {click_err}. Trying JS fallback...")
                        self.driver.execute_script("arguments[0].click();", next_button)
                        logging.info("✅ Clicked next month via JS.")
                except Exception as e:
                    logging.error(f"❌ Failed to click next month: {e}")
                    raise

                time.sleep(1)
                valid_dates = self.get_valid_date_buttons()

                if len(valid_dates) < 4:
                    raise Exception("❌ Not enough valid dates to form a 3-night stay.")

                random.shuffle(valid_dates)  # Randomize the list for variety
                for i in range(len(valid_dates) - 3):
                    try:
                        check_in = valid_dates[i]
                        check_in_text = check_in.text
                        check_in.click()
                        time.sleep(0.5)

                        # Re-fetch post DOM update
                        valid_after_click = self.get_valid_date_buttons()
                        if i + 3 >= len(valid_after_click):
                            continue  # Try next index

                        check_out = valid_after_click[i + 3]
                        check_out_text = check_out.text
                        check_out.click()

                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        logging.info(f"✅ Selected random dates: {check_in_text} to {check_out_text}")
                        return
                    except Exception as inner_e:
                        logging.warning(f"⚠️ Failed attempt at index {i}: {inner_e}")
                        continue

                raise Exception("❌ Could not find valid 4-day window in next month.")

            except Exception as e:
                logging.error(f"❌ Date selection failed: {e}")
                raise

        def set_room_occupants(self, adults=2, children=0, infants=0):
            try:
                self.wait.until(EC.element_to_be_clickable((By.ID, "search-engine-room-selection-button-Main"))).click()
                logging.info("✅ Clicked room selection button.")

                self.wait.until(EC.visibility_of_element_located((By.ID, "search-engine-room-selection-popover")))
                logging.info("✅ Room selection modal is visible.")

                def select_occupant(cell_id, value):
                    try:
                        container = self.driver.find_element(By.ID, cell_id)
                        dropdown_btn = container.find_element(By.CSS_SELECTOR, "button.sc-1da3f646-3")
                        self.driver.execute_script("arguments[0].click();", dropdown_btn)

                        # ✅ Wait for options to load
                        WebDriverWait(self.driver, 5).until(
                            lambda d: len(container.find_elements(By.CSS_SELECTOR, "button.sc-1da3f646-5")) > 0
                        )

                        options_container = container.find_element(By.CLASS_NAME, "sc-1da3f646-1")
                        options = options_container.find_elements(By.CSS_SELECTOR, "button.sc-1da3f646-5")

                        if not options:
                            raise Exception("❌ No options found inside dropdown.")

                        index = value if 0 <= value < len(options) else len(options) - 1
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", options[index])
                        self.driver.execute_script("arguments[0].click();", options[index])
                        logging.info(f"🔽 Set {cell_id} to {options[index].text}")

                    except Exception as e:
                        logging.error(f"❌ Failed to set {cell_id}: {e}")
                        raise

                # Set room configuration
                select_occupant("search-engine-build-room-room-row-cell-adults0", adults - 1)
                select_occupant("search-engine-build-room-room-row-cell-kids0", children)
                select_occupant("search-engine-build-room-room-row-cell-babies0", infants)

                continue_btn = self.driver.find_element(By.ID, "search-engine-build-room-next-button")
                self.driver.execute_script("arguments[0].click();", continue_btn)
                logging.info(f"✅ Room set: {adults} adults, {children} children, {infants} infants.")

            except Exception as e:
                logging.error(f"❌ Failed to select room occupants: {e}")
                self.take_screenshot("set_room_occupants_fail")
                raise

        # ✅ Click the 'חפש' (search) button
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
                    print(f"✅ Search button '{result}' clicked successfully.")
                else:
                    raise Exception("Search button not found on the page")
            except Exception as e:
                print(f"❌ Error clicking search button: {e}")
                raise

        # ✅ Get hotel link from search results by index
        def liked_hotel_links(self, hotel_index):
            return self.driver.find_elements(By.CSS_SELECTOR,
                'a.sc-b8919b5f-1.lgGiaA.sc-c2a74b5a-6.bMslGW[type="button"]'
            )[hotel_index]

        # ✅ Newsletter email field setter
        def news_letter_email_input(self, email_string):
            email = self.driver.find_element(By.CSS_SELECTOR, 'input#email')
            email.clear()
            email.send_keys(email_string)

        # ✅ Click newsletter register button
        def register_news_letter_button(self):
            self.driver.find_element(By.CSS_SELECTOR, 'button.sc-923ff82e-7.hVHcft').click()

        def close_post_login_popup(self):
            """Closes the popup/modal that appears after login."""
            try:
                popup_close_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sc-4a11a149-3.dVxqFs"))
                )
                self.driver.execute_script("arguments[0].click();", popup_close_btn)
                logging.info("✅ Post-login popup closed.")
            except TimeoutException:
                logging.info("ℹ️ No post-login popup appeared — skipping.")
            except Exception as e:
                logging.warning(f"❌ Failed to close post-login popup: {e}")
        # ✅ Footer button methods (legal, accessibility, etc.)
        # In FattalMainPage.py
        def take_screenshot(self, name="error_screenshot"):
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            screenshot_dir = os.path.join(os.getcwd(), "Screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            path = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
            self.driver.save_screenshot(path)
            logging.error(f"📸 Screenshot saved: {path}")

        def accessibility_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(1)').click()
        def customer_support_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(2)').click()
        def terms_of_use_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(3)').click()
        def privacy_policy_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(4)').click()
        def cancel_reservation_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(5)').click()
        def fattal_hotel_group_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(6)').click()
        def accessibility_statement_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(7)').click()
        def corporate_responsibility_button(self): self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR:nth-of-type(8)').click()
        def more_information_button(self): self.driver.find_element(By.CSS_SELECTOR, 'span.sc-68eae715-3.cmuwUL').click()
