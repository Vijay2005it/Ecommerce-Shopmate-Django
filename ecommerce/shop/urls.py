from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Home / Shop
    path('', views.shop_page, name='shop_page'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('vendor_dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),

    # Products
    path('add_product/', views.add_product, name='add_product'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/product/edit/<int:product_id>/', views.vendor_edit, name='vendor_edit'),

    # Cart
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout & Payment
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
    path('order_success/', views.order_success, name='order_success'),

    # Vendor Orders
    path('vendor/orders/', views.vendor_orders, name='vendor_orders'),

    # Admin Product Approval
    path('approve-product/<int:product_id>/', views.approve_product, name='approve_product'),
    path('reject-product/<int:product_id>/', views.reject_product, name='reject_product'),

    # Contact
    path('contact/', views.contact, name='contact'),

    path('orders/', views.orders_view, name='orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]