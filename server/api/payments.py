import requests
import logging
from django.conf import settings
from base64 import b64encode
from datetime import datetime

logger = logging.getLogger(__name__)


class MpesaClient:
    """Real Safaricom Daraja API client for M-Pesa STK Push."""

    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL

        # Switch between sandbox and production
        env = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')
        if env == 'production':
            self.base_url = "https://api.safaricom.co.ke"
        else:
            self.base_url = "https://sandbox.safaricom.co.ke"

    def get_token(self):
        """Authenticates with Safaricom OAuth to get a bearer token."""
        if not self.consumer_key or not self.consumer_secret:
            logger.error("M-Pesa credentials not configured")
            return None

        auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            response = requests.get(auth_url, auth=(self.consumer_key, self.consumer_secret), timeout=30)
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa token error: {e}")
            return None

    def stk_push(self, phone, amount, reference, description):
        """Initiates a real Lipa Na M-Pesa STK Push request."""
        token = self.get_token()
        if not token:
            return {"error": "Could not authenticate with M-Pesa. Check your API credentials."}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = b64encode(f"{self.shortcode}{self.passkey}{timestamp}".encode()).decode()

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": reference,
            "TransactionDesc": description
        }

        headers = {"Authorization": f"Bearer {token}"}
        endpoint = f"{self.base_url}/mpesa/stkpush/v1/processrequest"

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa STK Push error: {e}")
            return {"error": f"M-Pesa request failed: {str(e)}"}


class StripeClient:
    """Real Stripe API client using direct HTTP requests."""

    def __init__(self):
        self.api_key = settings.STRIPE_SECRET_KEY
        self.base_url = "https://api.stripe.com/v1"

    def create_payment_intent(self, amount, currency='kes'):
        """Creates a real Stripe PaymentIntent."""
        if not self.api_key:
            return {"error": "Stripe API key not configured. Set STRIPE_SECRET_KEY in your environment."}

        endpoint = f"{self.base_url}/payment_intents"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        # Stripe expects amount in the smallest currency unit (cents)
        payload = {
            "amount": int(amount * 100),
            "currency": currency,
            "payment_method_types[]": "card"
        }

        try:
            response = requests.post(endpoint, data=payload, headers=headers, timeout=30)
            data = response.json()
            if response.status_code != 200:
                logger.error(f"Stripe error: {data}")
                return {"error": data.get("error", {}).get("message", "Stripe payment failed")}
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Stripe request error: {e}")
            return {"error": f"Payment gateway unavailable: {str(e)}"}

    def confirm_payment(self, payment_intent_id):
        """Retrieves a PaymentIntent to check its status."""
        if not self.api_key:
            return {"error": "Stripe API key not configured"}

        endpoint = f"{self.base_url}/payment_intents/{payment_intent_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Stripe confirm error: {e}")
            return {"error": str(e)}
