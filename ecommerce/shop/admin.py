from django.contrib import admin
from .models import Product,Cart

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display =  ('id', 'name', 'price', 'vendor', 'created_at')
    list_filter = ('vendor',)
    search_fields = ('name','description')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'added_at')
    list_filter = ('user',)
    search_fields = ('product__name',)