from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order

class Command(BaseCommand):
    help = 'Clean up expired M-Pesa payments'
    
    def handle(self, *args, **options):
        expired_orders = Order.objects.filter(
            payment_method='M-Pesa',
            status='pending',
            payment_initiated_at__isnull=False
        )
        
        count = 0
        for order in expired_orders:
            if order.is_payment_expired():
                order.status = 'timeout'
                order.save()
                count += 1
                self.stdout.write(
                    self.style.WARNING(f'Marked order {order.id} as timeout')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {count} expired payments')
        )