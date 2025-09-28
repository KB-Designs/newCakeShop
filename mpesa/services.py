import requests
import base64
from datetime import datetime
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class MpesaService:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.env = settings.MPESA_ENV
        
        if self.env == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def get_access_token(self):
        """Get OAuth access token"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth_string = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_string}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.RequestException as e:
            logger.error(f"Error getting access token: {e}")
            return None
    
    def stk_push(self, phone, amount, order_id, description="Cake Purchase"):
        """Initiate STK Push request"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        
        # Format phone number (remove leading + or 0)
        phone = phone.lstrip('+').lstrip('0')
        if not phone.startswith('254'):
            phone = '254' + phone
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"ORDER{order_id}",
            "TransactionDesc": description
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()
            
            # Log the response (without sensitive data)
            logger.info(f"STK Push response for order {order_id}: {response_data}")
            
            return response_data
        except requests.RequestException as e:
            logger.error(f"Error in STK Push: {e}")
            return None