import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Order, OrderItem
from cart.cart import Cart

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
                # For now, simulate M-Pesa payment success
                # In production, you'd integrate with M-Pesa API here
                order.status = 'paid'
                order.save()
                cart.clear()
                messages.success(request, "M-Pesa payment initiated successfully!")
                return redirect('orders:success', order_id=order.id)
                
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

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'orders/success.html', context)

def get_county_stations(request):
    county = request.GET.get('county')
    stations = COUNTY_STATIONS.get(county, [])
    return JsonResponse({'stations': stations})