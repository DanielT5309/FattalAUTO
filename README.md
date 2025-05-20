# Fattal Automation Tests

This project contains end-to-end Selenium tests for the Fattal hotel booking website.
It includes page objects for both desktop and mobile flows and a collection of
`unittest`/`pytest` suites that automate common booking scenarios.

## Directory structure

- `Fattal_Pages/` – page object models for the desktop site
- `Mobile_Fattal_Pages/` – page object models for the mobile site
- `Fattal_Tests/` – test suites
- `conftest.py` – test configuration helpers
- `pytest.ini` – pytest configuration
- `requirements.txt` – python dependencies

## Installation

Create a virtual environment and install the requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables

Tests rely on several environment variables. These are typically loaded from a
`.env` file using `python-dotenv`.

Required variables include:

- `ENV_ACTIVE` – base URL of the environment under test
- `DEFAULT_EMAIL`, `DEFAULT_PHONE`, `DEFAULT_FIRST_NAME`, `DEFAULT_LAST_NAME` – default guest details
- `DEFAULT_FIRST_NAME_ENGLISH`, `DEFAULT_LAST_NAME_ENGLISH` – default guest details for the English site
- `DEFAULT_HOTEL_NAME`, `DEFAULT_HOTEL_NAME_EUROPE` – default hotel names
- `PAYMENT_CARD_NUMBER`, `PAYMENT_CARDHOLDER_NAME`, `PAYMENT_EXPIRY_MONTH`, `PAYMENT_EXPIRY_YEAR`, `PAYMENT_CVV`, `PAYMENT_ID_NUMBER` – credit card details used in tests
- `GIFT1`, `GIFT2`, `GIFT3`, `GIFT4` – gift codes
- `CLUB_RENEW_ID`, `CLUB_RENEW_PASSWORD`
- `CLUB_ABOUT_EXPIRE_ID`, `CLUB_ABOUT_EXPIRE_PASSWORD`
- `CLUB_ABOUT_EXPIRE_ID_FORM`, `CLUB_ABOUT_EXPIRE_PASSWORD_FORM`
- `CLUB_11NIGHT_ID`, `CLUB_11NIGHT_PASSWORD`
- `CLUB_11NIGHT_ID_EUROPE`, `CLUB_11NIGHT_PASSWORD_EUROPE`
- `CLUB_REGULAR_ID`, `CLUB_REGULAR_PASSWORD`
- `EMPLOYEE_COUPON_ID`

## Running the tests

Activate your environment with the variables above and run:

```bash
pytest
```

You can also execute the custom ordered suite:

```bash
python Fattal_Tests/test_Suit.py
```
