import requests
import os
from sheets import FlightDeals
from sheets import city_price
from twilio.rest import Client
from dotenv import load_dotenv
from req_token import InitializeToken

# Load environment variables from .env file
load_dotenv()

account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("ACCOUNT_TOKEN")

# Initialize Token for Amadeus API
token = InitializeToken()
access_token = token.get_access_token()  # FIXED: use access_token here

# Initialize FlightDeals Object
flight_deals = FlightDeals()

# Get city-price mapping
cities = flight_deals.city_price_dict()

# Amadeus API endpoint
URL = "https://test.api.amadeus.com/v1/shopping/flight-destinations"

params = {
    "origin": "LON",
    "maxPrice": 1000
}

headers = {
    'Authorization': f'Bearer {access_token}'  # FIXED: use access_token instead of Twilio token
}

try:
    response = requests.get(url=URL, params=params, headers=headers)
    response.raise_for_status()  # will raise error if not 200
    flight_data = response.json()

    for destination in flight_data.get("data", []):
        dest_code = destination["destination"]
        dest_price = float(destination["price"]["total"])

        if dest_code in cities and dest_price < cities[dest_code]:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                from_="+14155238886",
                body=f"Lower Price Alert! ✈️ Destination: {dest_code} | Price: {dest_price}",
                to="+17164631835"
            )
            print(f"Message sent: {message.sid}")

    print("Completed flight check.")
except requests.exceptions.RequestException as e:
    print(f"API Request failed: {e}")
except Exception as e:
    print(f"Error: {e}")
