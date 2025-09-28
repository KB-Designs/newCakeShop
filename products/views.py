from django.shortcuts import render, get_object_or_404
from .models import Product, Category, EggOption

def product_list(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)
    
    selected_category_name = None
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        selected_category_name = category.name
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'selected_category_name': selected_category_name,
    }
    return render(request, 'products/list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    egg_options = EggOption.objects.all()
    
    context = {
        'product': product,
        'egg_options': egg_options,
    }
    return render(request, 'products/detail.html', context)