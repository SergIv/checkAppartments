import time
from xmlrpc.client import DateTime

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BOT_TOKEN = '6652675442:AAGqAIDxjw4eu4nblbvj1KvwCm1lCOzwU8w'  # @GreatFamilyHelper_bot
CHAT_ID = '-1002293667480'  # Great Family Chat
#CHAT_ID = '436351982"  # Serg

APP_URL = "https://vantagerent.pl/wyszukaj-mieszkanie/?lang=pl&pg=1&posts_per_page=10&layout=list&city_id=8&display_starred=1&number_of_rooms%5B0%5D=4&sort_value=local_available_from&sort_direction=ASC"

def send_telegram_message(message, silent=False):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': message,
        'disable_notification': silent  # Add parameter for silent message
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Telegram message sent successfully!")
        else:
            print(f"Failed to send message. Error: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Function to get the full HTML content of the target <div> using Playwright
def fetch_apartment_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Set the timeout to handle longer page loading times
        page.goto(APP_URL, timeout=30000)  # 30 seconds timeout

        # Wait until the network is idle, meaning no more network requests are being made
        page.wait_for_load_state('networkidle', timeout=30000)  # Adjust timeout if needed

        # Optional: Add a sleep to allow extra time for JavaScript to load content after network idle
        time.sleep(5)  # Sleep for 5 seconds to give the page time to render content

        # Check if content is loaded inside the div
        try:
            # Optionally, wait for a specific element or text that confirms the data is fully loaded
            page.wait_for_selector("#js-locals-table div, #js-locals-table span", timeout=30000)
        except Exception as e:
            print(f"No appartments in selected filter. Selector wait failed: {e}")
            send_telegram_message("Error: Data fetching failed.  No data available by filter", silent=True)
            browser.close()
            return "None"

        # Extract the full HTML content of the target <div>
        content = page.inner_html("#js-locals-table")
#debug        print("Fetched content: ", content)
        browser.close()

        return content


# Function to check for changes in the data
def check_for_changes():
    # Initial data stored (replace with loading from a file or database if needed)
    try:
        with open("stored_data.txt", "r") as file:
            stored_data = file.read()
    except FileNotFoundError:
        stored_data = ""

    # Fetch current data from the webpage
    current_data = fetch_apartment_data()
#debug    print("current_data = ", current_data)

    if current_data and current_data != stored_data:
        print("Data has changed!")
        send_telegram_message(f"Available apartments have changed! Check here - {APP_URL}")
        # Save the new data for future comparisons
        with open("stored_data.txt", "w") as file:
            file.write(current_data)
    else:
        print("No changes detected.")
        send_telegram_message("No Changes", True)


# Main function to periodically check for updates
if __name__ == "__main__":
    while True:
        check_for_changes()
        time.sleep(900)  # Check every 15 min (900) / or hour (3600)
