from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from products.models import Product, SizeVariant, IcingOption, EggOption
from .cart import Cart

def cart_detail(request):
    return render(request, 'cart/detail.html')

def cart_add(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        size_slug = request.POST.get('size')
        icing_slug = request.POST.get('icing')
        eggs_slug = request.POST.get('eggs')
        message = request.POST.get('message', '')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        size = SizeVariant.objects.filter(slug=size_slug, product=product).first() if size_slug else None
        icing = IcingOption.objects.filter(slug=icing_slug, product=product).first() if icing_slug else None
        eggs = EggOption.objects.filter(slug=eggs_slug).first() if eggs_slug else None
        
        cart = Cart(request)
        cart.add(product, size, eggs, icing, message, quantity)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': len(cart),
                'cart_total': cart.get_total()
            })
        
        return redirect('cart:detail')
    
    return redirect('products:list')

def cart_remove(request):
    if request.method == 'POST':
        key = request.POST.get('key')
        cart = Cart(request)
        cart.remove(key)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': len(cart),
                'cart_total': cart.get_total()
            })
        
        return redirect('cart:detail')
    
    return redirect('cart:detail')

def cart_update(request):
    if request.method == 'POST':
        key = request.POST.get('key')
        quantity = int(request.POST.get('quantity', 1))
        
        cart = Cart(request)
        cart.update(key, quantity)
        
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total': cart.get_total()
        })
    
    return JsonResponse({'success': False})