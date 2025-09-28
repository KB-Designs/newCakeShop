import hashlib
from decimal import Decimal
from django.conf import settings
from products.models import Product, SizeVariant, IcingOption, EggOption

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def _generate_key(self, product_id, size_slug, eggs_slug, icing_slug, message):
        """Generate unique key for cart item"""
        message_hash = hashlib.md5(message.encode()).hexdigest()[:8] if message else 'no-message'
        return f"{product_id}-{size_slug}-{eggs_slug}-{icing_slug}-{message_hash}"
    
    def add(self, product, size, eggs, icing, message, quantity=1):
        """Add item to cart or update quantity"""
        product_id = str(product.id)
        size_slug = size.slug if size else 'no-size'
        eggs_slug = eggs.slug if eggs else 'no-eggs'
        icing_slug = icing.slug if icing else 'no-icing'
        
        key = self._generate_key(product_id, size_slug, eggs_slug, icing_slug, message)
        
        # Calculate unit price
        unit_price = Decimal('0')
        if size:
            unit_price = size.price
        else:
            unit_price = product.base_price
        
        if icing:
            unit_price += icing.price_modifier
        
        if eggs:
            unit_price += eggs.price_modifier
        
        if key in self.cart:
            # Update quantity
            self.cart[key]['quantity'] += quantity
        else:
            # Add new item
            self.cart[key] = {
                'product_id': product_id,
                'product_name': product.name,
                'size_name': size.name if size else '',
                'size_slug': size_slug,
                'eggs_name': eggs.name if eggs else '',
                'eggs_slug': eggs_slug,
                'icing_name': icing.name if icing else '',
                'icing_slug': icing_slug,
                'message': message,
                'unit_price': str(unit_price),
                'quantity': quantity,
            }
        
        self.cart[key]['total_price'] = str(unit_price * self.cart[key]['quantity'])
        self.save()
    
    def update(self, key, quantity):
        """Update item quantity"""
        if key in self.cart:
            if quantity <= 0:
                self.remove(key)
            else:
                unit_price = Decimal(self.cart[key]['unit_price'])
                self.cart[key]['quantity'] = quantity
                self.cart[key]['total_price'] = str(unit_price * quantity)
                self.save()
    
    def remove(self, key):
        """Remove item from cart"""
        if key in self.cart:
            del self.cart[key]
            self.save()
    
    def __iter__(self):
        """Iterate through cart items"""
        cart = self.cart.copy()
        for key, item in cart.items():
            item['key'] = key
            item['unit_price'] = Decimal(item['unit_price'])
            item['total_price'] = Decimal(item['total_price'])
            yield item
    
    def __len__(self):
        """Return total quantity of items in cart"""
        try:
            return sum(int(item['quantity']) for item in self.cart.values())
        except (KeyError, ValueError):
            return 0
    
    def get_total(self):
        """Return total cart value"""
        try:
            return sum(Decimal(item['total_price']) for item in self.cart.values())
        except (KeyError, ValueError):
            return Decimal('0')
    
    def clear(self):
        """Empty cart"""
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()
    
    def save(self):
        """Mark session as modified"""
        self.session.modified = True