import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env
load_dotenv()

# === Environment Variables ===
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
SHEETY_TOKEN = os.getenv("SHEETY_TOKEN")
TWILIO_SID = os.getenv("ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("ACCOUNT_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")  # Example: "+14155238886"
TWILIO_TO = os.getenv("TWILIO_TO")      # Example: "+91xxxxxxxxxx"

# === Get Amadeus Access Token ===
def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        print(f"[Token Error] {e}")
        return None

# === Get City-Price Data from Sheety ===
def get_city_price_map():
    url = "https://api.sheety.co/967904ee9fe8cf7c6db7480d06a3bc63/day39CapstoneFlightDeals/prices"
    headers = {
        "Authorization": f"Basic {SHEETY_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {
            item["iataCode"]: item["highestPrice"]
            for item in data.get("prices", [])
        }
    except requests.RequestException as e:
        print(f"[Sheety Error] {e}")
        return {}

# === Main Flight Deal Finder ===
def check_flight_deals():
    access_token = get_amadeus_token()
    if not access_token:
        print("Failed to retrieve Amadeus token.")
        return

    city_prices = get_city_price_map()
    if not city_prices:
        print("No city price data found.")
        return

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
                msg = client.messages.create(
                    from_=TWILIO_FROM,
                    to=TWILIO_TO,
                    body=msg_body
                )
                print(f"Alert sent: {msg.sid}")

        print("✅ Flight check complete.")

    except requests.RequestException as e:
        print(f"[Flight API Error] {e}")

# === Run Script ===
if __name__ == "__main__":
    check_flight_deals()
