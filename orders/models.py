from django.db import models
from decimal import Decimal

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('M-Pesa', 'M-Pesa'),
        ('COD', 'Cash on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('fulfilled', 'Fulfilled'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    county = models.CharField(max_length=100)
    pickup_station = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    checkout_request_id = models.CharField(max_length=100, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.first_name} {self.last_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')  # Add related_name
    size = models.CharField(max_length=50, blank=True)
    icing = models.CharField(max_length=100, blank=True)
    eggs = models.CharField(max_length=50, blank=True)
    custom_message = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.unit_price * Decimal(self.quantity)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product_name} - {self.quantity}"