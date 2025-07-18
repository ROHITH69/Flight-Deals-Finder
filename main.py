import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client
from amadeus_token_manager import AmadeusTokenManager
from flight_sheet_client import FlightSheetClient

# Load environment variables
load_dotenv()

# === Environment Variables ===
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
TWILIO_SID = os.getenv("ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("ACCOUNT_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")

def check_flight_deals():
    # Get Amadeus access token
    token_manager = AmadeusTokenManager(AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET)
    access_token = token_manager.fetch_token()
    if not access_token:
        print("❌ Failed to retrieve Amadeus access token.")
        return

    # Get city-price map from Google Sheet
    sheet_client = FlightSheetClient()
    city_prices = sheet_client.fetch_city_price_map()
    if not city_prices:
        print("❌ No city price data found.")
        return

    # Amadeus API to search for deals
    url = "https://test.api.amadeus.com/v1/shopping/flight-destinations"
    params = {
        "origin": "LON",
        "maxPrice": 1000
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        flights = response.json().get("data", [])

        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

        for flight in flights:
            code = flight.get("destination")
            price = float(flight.get("price", {}).get("total", 0))

            if code in city_prices and price < city_prices[code]:
                msg_body = f"✈️ Deal Found! {code} at ₹{price} (was ₹{city_prices[code]})"
                message = client.messages.create(
                    from_=TWILIO_FROM,
                    to=TWILIO_TO,
                    body=msg_body
                )
                print(f"✅ Alert sent: {message.sid}")

        print("✅ Flight check complete.")

    except requests.RequestException as e:
        print(f"[Flight API Error] {e}")

if __name__ == "__main__":
    check_flight_deals()
