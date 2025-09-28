from django.shortcuts import render
from products.models import Product, Category

def home(request):
    featured_products = Product.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()[:4]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'shop/index.html', context)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render(request, 'shop/contact.html')