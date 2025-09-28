import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            logger.info(f"M-Pesa callback received: {callback_data}")
            
            # Extract callback metadata
            result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            result_desc = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
            checkout_request_id = callback_data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            
            # Find the order
            try:
                order = Order.objects.get(checkout_request_id=checkout_request_id)
            except Order.DoesNotExist:
                logger.error(f"Order not found for checkout_request_id: {checkout_request_id}")
                return JsonResponse({'result': 'error', 'message': 'Order not found'})
            
            if result_code == 0:
                # Payment successful
                callback_metadata = callback_data['Body']['stkCallback']['CallbackMetadata']['Item']
                
                # Extract transaction details
                transaction_data = {}
                for item in callback_metadata:
                    transaction_data[item['Name']] = item.get('Value')
                
                order.status = 'paid'
                order.transaction_id = transaction_data.get('MpesaReceiptNumber', '')
                order.save()
                
                logger.info(f"Payment successful for order {order.id}, transaction: {order.transaction_id}")
            else:
                # Payment failed
                order.status = 'failed'
                order.save()
                logger.warning(f"Payment failed for order {order.id}: {result_desc}")
            
            return JsonResponse({'result': 'success'})
            
        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {e}")
            return JsonResponse({'result': 'error', 'message': str(e)})
    
    return JsonResponse({'result': 'error', 'message': 'Method not allowed'})

def stk_push(request):
    """Trigger STK Push (for testing)"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = int(request.POST.get('amount'))
        order_id = request.POST.get('order_id')
        
        from .services import MpesaService
        mpesa_service = MpesaService()
        response = mpesa_service.stk_push(phone, amount, order_id)
        
        return JsonResponse(response or {'error': 'Failed to initiate payment'})
    
    return JsonResponse({'error': 'Method not allowed'})