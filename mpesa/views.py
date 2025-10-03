import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from orders.models import Order
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class MpesaCallbackView(View):
    """Handle M-Pesa callback"""
    
    def post(self, request):
        try:
            # Log the raw request body for debugging
            raw_body = request.body.decode('utf-8')
            logger.info(f"Raw M-Pesa callback received: {raw_body}")
            
            callback_data = json.loads(raw_body)
            logger.info(f"Parsed M-Pesa callback: {json.dumps(callback_data, indent=2)}")
            
            # Extract callback metadata
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            merchant_request_id = stk_callback.get('MerchantRequestID')
            
            logger.info(f"Processing callback - CheckoutRequestID: {checkout_request_id}, ResultCode: {result_code}")
            
            # Find the order
            order = None
            if checkout_request_id:
                try:
                    order = Order.objects.get(checkout_request_id=checkout_request_id)
                except Order.DoesNotExist:
                    logger.warning(f"Order not found for checkout_request_id: {checkout_request_id}")
            
            if not order and merchant_request_id:
                try:
                    order = Order.objects.get(checkout_request_id=merchant_request_id)
                except Order.DoesNotExist:
                    logger.warning(f"Order not found for merchant_request_id: {merchant_request_id}")
            
            if not order:
                logger.error("No order found for callback")
                return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})  # Still return success to M-Pesa
            
            # Handle different result codes
            if result_code == 0:
                # Payment successful
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                
                # Extract transaction details
                transaction_data = {}
                for item in callback_metadata:
                    transaction_data[item.get('Name')] = item.get('Value')
                
                mpesa_receipt_number = transaction_data.get('MpesaReceiptNumber')
                phone_number = transaction_data.get('PhoneNumber')
                amount = transaction_data.get('Amount')
                
                order.status = 'paid'
                order.transaction_id = mpesa_receipt_number or ''
                order.save()
                
                logger.info(f"Payment successful for order {order.id}")
                logger.info(f"Transaction ID: {mpesa_receipt_number}, Amount: {amount}")
                
            elif result_code == 1:
                # Insufficient funds
                order.status = 'failed'
                order.save()
                logger.warning(f"Payment failed - Insufficient funds for order {order.id}")
                
            elif result_code == 1032:
                # Request cancelled by user
                order.status = 'cancelled'
                order.save()
                logger.info(f"Payment cancelled by user for order {order.id}")
                
            elif result_code == 1037:
                # Timeout - user didn't enter PIN
                order.status = 'timeout'
                order.save()
                logger.info(f"Payment timeout - user didn't enter PIN for order {order.id}")
                
            elif result_code == 1031:
                # Request rejected by user
                order.status = 'cancelled'
                order.save()
                logger.info(f"Payment rejected by user for order {order.id}")
                
            else:
                # Other errors
                order.status = 'failed'
                order.save()
                logger.warning(f"Payment failed for order {order.id}: {result_desc} (Code: {result_code})")
            
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in callback: {e}")
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Failed - Invalid JSON'})
        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {e}")
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Failed - Server error'})


@csrf_exempt
def stk_push(request):
    """Trigger STK Push (for testing)"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body) if request.body else {}
            phone = data.get('phone') or request.POST.get('phone')
            amount = data.get('amount') or request.POST.get('amount')
            order_id = data.get('order_id') or request.POST.get('order_id')
            
            if not all([phone, amount, order_id]):
                return JsonResponse({'error': 'Missing required parameters: phone, amount, order_id'})
            
            from .services import MpesaService
            mpesa_service = MpesaService()
            response = mpesa_service.stk_push(phone, float(amount), order_id)
            
            return JsonResponse(response)
            
        except Exception as e:
            logger.error(f"Error in STK Push view: {e}")
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Method not allowed'})