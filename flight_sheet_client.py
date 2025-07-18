import os
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

class FlightSheetClient:
    def __init__(self):
        self.endpoint = "https://api.sheety.co/967904ee9fe8cf7c6db7480d06a3bc63/day39CapstoneFlightDeals/prices"
        self.headers = {
            "Authorization": f"Basic {os.getenv('SHEETY_TOKEN')}"
        }

    def fetch_city_price_map(self):
        """Returns a dictionary of IATA codes mapped to their max prices."""
        try:
            response = requests.get(self.endpoint, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return {
                item["iataCode"]: item["highestPrice"]
                for item in data.get("prices", [])
            }

        except requests.exceptions.RequestException as e:
            print(f"[Sheet Fetch Error] {e}")
            return {}
