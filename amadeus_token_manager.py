import requests
import logging

class AmadeusTokenManager:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        self.token = None

    def fetch_token(self):
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.post(self.token_url, data=payload, headers=headers)
            response.raise_for_status()
            self.token = response.json().get("access_token")
            return self.token

        except requests.exceptions.RequestException as err:
            logging.error(f"Token request failed: {err}")
            return None
