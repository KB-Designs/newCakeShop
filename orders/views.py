import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem
from cart.cart import Cart
from mpesa.services import MpesaService

# County and station data
COUNTY_STATIONS = {
    'Nairobi': ['Westgate Mall', 'Garden City Mall', 'The Hub Karen', 'Two Rivers Mall'],
    'Mombasa': ['Nyali Centre', 'City Mall', 'Mtwapa', 'Likoni'],
    'Kisumu': ['West End Mall', 'Kisumu Mega Plaza', 'Kisumu CBD'],
    'Nakuru': ['Westside Mall', 'Nakuru Town', 'Lanet'],
}

def checkout(request):
    cart = Cart(request)
    
    # Redirect if cart is empty
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Add some items before checkout.")
        return redirect('cart:detail')
    
    if request.method == 'POST':
        try:
            # Create order
            order = Order.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                phone=request.POST.get('phone'),
                email=request.POST.get('email'),
                county=request.POST.get('county'),
                pickup_station=request.POST.get('pickup_station'),
                payment_method=request.POST.get('payment_method'),
                total=cart.get_total(),
            )
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product_name=item['product_name'],
                    product_id=item['product_id'],
                    size=item['size_name'],
                    icing=item['icing_name'],
                    eggs=item['eggs_name'],
                    custom_message=item['message'],
                    unit_price=item['unit_price'],
                    quantity=item['quantity'],
                    total_price=item['total_price'],
                )
            
            # Handle payment based on method
            if order.payment_method == 'M-Pesa':
                # Set payment initiation time
                order.payment_initiated_at = timezone.now()
                order.save()
                
                # Initialize M-Pesa service
                mpesa_service = MpesaService()
                
                # Trigger STK Push
                response = mpesa_service.stk_push(
                    phone=order.phone,
                    amount=order.total,
                    order_id=order.id
                )
                
                if response.get('ResponseCode') == '0':
                    # STK Push initiated successfully
                    order.checkout_request_id = response.get('CheckoutRequestID')
                    order.save()
                    
                    messages.success(request, "M-Pesa payment initiated! Check your phone to complete payment.")
                    return redirect('orders:success', order_id=order.id)
                    
                else:
                    # STK Push failed
                    error_message = response.get('error') or response.get('ResponseDescription') or 'Payment initiation failed'
                    order.status = 'failed'
                    order.save()
                    
                    messages.error(request, f"M-Pesa payment failed: {error_message}")
                    return redirect('cart:detail')
                    
            else:  # Cash on Delivery
                order.status = 'pending'
                order.save()
                cart.clear()
                messages.success(request, "Order placed successfully! Pay when you pickup.")
                return redirect('orders:success', order_id=order.id)
                
        except Exception as e:
            messages.error(request, f"Error processing order: {str(e)}")
            return redirect('cart:detail')
    
    # GET request - show checkout form
    context = {
        'counties': list(COUNTY_STATIONS.keys())
    }
    return render(request, 'orders/checkout.html', context)


# ... (keep the existing COUNTY_STATIONS and checkout function)

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # If this is an M-Pesa order and payment was just initiated, set the initiation time
    if order.payment_method == 'M-Pesa' and order.status == 'pending' and not order.payment_initiated_at:
        order.payment_initiated_at = timezone.now()
        order.save()
        
    context = {
        'order': order,
    }
    return render(request, 'orders/success.html', context)

def get_county_stations(request):
    county = request.GET.get('county')
    stations = COUNTY_STATIONS.get(county, [])
    return JsonResponse({'stations': stations})

def payment_status(request, order_id):
    """API endpoint to check payment status"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if payment has expired (10 minutes)
    if order.payment_method == 'M-Pesa' and order.status == 'pending' and order.is_payment_expired():
        order.status = 'timeout'
        order.save()
    
    return JsonResponse({
        'status': order.status,
        'status_display': order.get_status_display(),
        'transaction_id': order.transaction_id,
        'payment_method': order.payment_method,
        'is_expired': order.is_payment_expired() if order.status == 'pending' else False,
    })

def simulate_payment_cancel(request, order_id):
    """Endpoint to simulate payment cancellation (for testing)"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.status = 'cancelled'
        order.save()
        return JsonResponse({'success': True, 'status': 'cancelled'})
    return JsonResponse({'error': 'Method not allowed'})