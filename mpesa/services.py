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
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting access token: {e}")
            logger.error(f"Response: {getattr(e, 'response', None)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting access token: {e}")
            return None
    
    def stk_push(self, phone, amount, order_id, description="Cake Purchase"):
        """Initiate STK Push request"""
        access_token = self.get_access_token()
        if not access_token:
            logger.error("Failed to get access token")
            return {'error': 'Failed to get access token'}
        
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        
        # Format phone number (remove leading + or 0)
        phone = str(phone).lstrip('+').lstrip('0')
        if not phone.startswith('254'):
            if len(phone) == 9:  # Local number without 254
                phone = '254' + phone
            elif len(phone) == 10:  # Number with leading 0
                phone = '254' + phone[1:]
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
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
            logger.info(f"Sending STK Push request for order {order_id}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response_data = response.json()
            
            logger.info(f"STK Push response for order {order_id}: {json.dumps(response_data, indent=2)}")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in STK Push request: {e}")
            logger.error(f"Response: {getattr(e, 'response', None)}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in STK Push: {e}")
            return {'error': str(e)}