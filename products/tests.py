from django.test import TestCase
from django.urls import reverse
from .models import Category, Product, SizeVariant

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Birthday Cakes",
            slug="birthday-cakes"
        )
        self.product = Product.objects.create(
            name="Chocolate Cake",
            slug="chocolate-cake",
            description="Delicious chocolate cake",
            base_price=1500.00,
            category=self.category
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Chocolate Cake")
        self.assertEqual(self.product.base_price, 1500.00)
        self.assertTrue(self.product.is_active)
