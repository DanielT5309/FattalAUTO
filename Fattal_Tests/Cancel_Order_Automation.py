import json
import requests

CANCEL_URL = "https://fattal.custhelp.com/cgi-bin/fattal.cfg/php/custom/runservice2.php"
RUNSCRIPT_PARAM = "cancel_order.php"
ORDERS_FILE = "orders_to_cancel.json"

# 🔐 Credentials — fill in with real ones or load from .env
HEADERS = {
    "USERNAME": "qa_automation",
    "PASSWORD": "vFqUpy3.4hwfr99vCN2-",
    "Content-Type": "application/json"
}


def cancel_order(master_id, hotel_id):
    payload = {
        "masterID": master_id,
        "hotelID": hotel_id
    }

    try:
        response = requests.post(
            url=f"{CANCEL_URL}?runscript={RUNSCRIPT_PARAM}",
            headers=HEADERS,
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            print(f" Order {master_id} at Hotel {hotel_id} cancelled successfully.")
        else:
            print(f" Failed to cancel Order {master_id}: HTTP {response.status_code} — {response.text}")
    except Exception as e:
        print(f" Exception while cancelling Order {master_id}: {e}")


def run_bulk_cancellation():
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
    except Exception as e:
        print(f" Could not load orders from JSON: {e}")
        return

    for order in orders:
        master_id = order.get("masterID")
        hotel_id = order.get("hotelID")

        if master_id and hotel_id:
            cancel_order(master_id, hotel_id)
        else:
            print(f" Invalid entry skipped: {order}")


if __name__ == "__main__":
    run_bulk_cancellation()
