from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product_name', 'unit_price', 'quantity', 'total_price']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone', 'total', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'county', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    actions = ['mark_as_paid', 'mark_as_fulfilled']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
    mark_as_paid.short_description = "Mark selected orders as paid"
    
    def mark_as_fulfilled(self, request, queryset):
        queryset.update(status='fulfilled')
    mark_as_fulfilled.short_description = "Mark selected orders as fulfilled"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['order__status']
    search_fields = ['product_name', 'order__id']