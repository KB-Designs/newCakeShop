from django.contrib import admin
from .models import Category, Product, SizeVariant, IcingOption, EggOption

class SizeVariantInline(admin.TabularInline):
    model = SizeVariant
    extra = 1

class IcingOptionInline(admin.TabularInline):
    model = IcingOption
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']  # Now created_at exists
    list_editable = ['base_price', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    inlines = [SizeVariantInline, IcingOptionInline]

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'price']
    list_filter = ['product']
    search_fields = ['product__name', 'name']

@admin.register(IcingOption)
class IcingOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'price_modifier']
    list_filter = ['product']
    search_fields = ['name', 'product__name']

@admin.register(EggOption)
class EggOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price_modifier']
    prepopulated_fields = {'slug': ('name',)}