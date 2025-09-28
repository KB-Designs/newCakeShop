from .cart import Cart

def cart(request):
    try:
        return {'cart': Cart(request)}
    except Exception:
        # Return empty cart if there's any issue
        return {'cart': []}