from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, LoginForm,OrderForm,Orders
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cart, OrderItem, Product,Orders,Contact,CustomUser
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import  User

# =======================
# Register View
# =======================
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Encrypt password
            user.save()
            login(request, user)

            if user.user_type == 'admin':
                return redirect('shop:admin_dashboard')
            elif user.user_type == "vendor":
                return redirect('shop:vendor_dashboard')
            else:
                return redirect('shop:user_dashboard')
    else:
        form = RegisterForm()

    return render(request, 'shop/register.html', {'form': form})


# =======================
# Login View
# =======================
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if user.user_type == 'admin':
                    return redirect('shop:admin_dashboard')
                elif user.user_type == "vendor":
                    return redirect('shop:vendor_dashboard')
                else:
                    return redirect('shop:user_dashboard')
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, 'shop/login.html', {'form': form})


# =======================
# Logout
# =======================
def logout_view(request):
    logout(request)
    return redirect("shop:login")


# =======================
# Dashboards
# =======================
@login_required(login_url='shop:login')
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('shop:login')

    pending_products = Product.objects.filter(is_approved=False)
    recent_orders = Orders.objects.all().order_by('-created_at')[:5]

    total_users = CustomUser.objects.count()
    total_vendors = CustomUser.objects.filter(user_type='vendor').count()
    total_customers = CustomUser.objects.filter(user_type='user').count()

    total_products = Product.objects.count()
    approved_products = Product.objects.filter(is_approved=True).count()
    pending_products_count = pending_products.count()

    from django.db.models import Sum, F
    total_revenue = OrderItem.objects.aggregate(
        revenue=Sum(F('quantity') * F('product__price'))
    )['revenue'] or 0

    total_items_sold = OrderItem.objects.aggregate(total=Sum('quantity'))['total'] or 0
    total_items_in_carts = Cart.objects.aggregate(total=Sum('quantity'))['total'] or 0

    messages_list = Contact.objects.all()


    context = {
        'pending_products': pending_products,
        'recent_orders': recent_orders,
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_customers': total_customers,
        'total_products': total_products,
        'approved_products': approved_products,
        'pending_products_count': pending_products_count,
        'total_revenue': total_revenue,
        'total_items_sold': total_items_sold,
        'total_items_in_carts': total_items_in_carts,
        'messages':messages_list
    }
    return render(request, 'shop/admin_dashboard.html', context)



@login_required(login_url='shop:login')
def vendor_dashboard(request):
    return render(request, 'shop/vendor_dashboard.html')


@login_required(login_url='shop:login')
def user_dashboard(request):
    return render(request, 'shop/user_dashboard.html')


# =======================
# Add Product (Vendor)
# =======================
@login_required(login_url='shop:login')
def add_product(request):
    if request.method == "POST":
        name = request.POST['name']
        quantity = request.POST['quantity']
        description = request.POST['description']
        price = request.POST['price']
        image = request.FILES['image']

        Product.objects.create(
            name=name,
            quantity=quantity,
            status='inactive',
            description=description,
            price=price,
            image=image,
            vendor=request.user,
            is_approved=False,
        )
        messages.success(request, "Product added successfully and waiting for admin approval.")
        return redirect('shop:vendor_dashboard')

    return render(request, 'shop/add_product.html')


# =======================
# Shop Page (Only approved products)
# =======================
def shop_page(request):
    products = Product.objects.all().filter(is_approved=True)
    return render(request, "shop/shop_page.html", {'products': products})

# =======================
# Add to Cart (Only approved products)
# =======================
@login_required(login_url='shop:login')
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id, is_approved=True)
    except Product.DoesNotExist:
        messages.error(request, "This product is not available or not approved yet.")
        return redirect('shop:shop_page')

    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'"{product.name}" added to cart.')
    return redirect('shop:cart_page')

# =======================
# Update Cart
# =======================
@login_required(login_url='shop:login')
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = Product.objects.get(id=product_id)

        cart_item = Cart.objects.get(user=request.user, product=product)
        cart_item.quantity = quantity
        cart_item.save()

    return redirect('shop:cart_page')

# =======================
# Remove from Cart
# =======================
@login_required(login_url='shop:login')
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        Cart.objects.filter(user=request.user, product=product).delete()

    return redirect('shop:cart_page')

# =======================
# Approve Product (Admin only)
# =======================


@login_required(login_url='shop:login')
def approve_product(request, product_id):
    if request.user.user_type != "admin":
        messages.error(request, "You do not have permission to approve products.")
        return redirect('shop:login')

    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        product.status = 'active'
        product.is_approved = True
        product.save()
        messages.success(request, f'Product "{product.name}" approved successfully.')

    return redirect('shop:admin_dashboard')



@login_required(login_url='shop:login')
def reject_product(request, product_id):
    if request.user.user_type != "admin":
        messages.error(request, "You do not have permission to reject products.")
        return redirect('shop:login')

    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, f'Product "{product.name}" rejected successfully.')

    return redirect('shop:admin_dashboard')
    
@login_required(login_url='shop:login')
def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum([item.total_price() for item in cart_items])
    total_items = sum([item.quantity for item in cart_items])  # total quantity of items
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'total_items': total_items
    })

# =======================
# Checkout
# =======================
@login_required(login_url='shop:login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum([item.product.price * item.quantity for item in cart_items])

    if request.method == "POST":
        # redirect to payment page without deleting cart yet
        return redirect('shop:payment')

    return render(request, 'shop/checkout.html', {'cart_items': cart_items, 'total': total})



@login_required(login_url='shop:login')
def payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    if request.method == "POST":
        data = request.POST
        order = Orders.objects.create(
            user=request.user,  
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            address=data.get('address'),
            country=data.get('country'),
            state=data.get('state'),
            pin_code=data.get('pin_code'),
            payment_method=data.get('payment_method'),
            bank_on_card=data.get('name_on_card'),
            card_number=data.get('card_number'),
            expiration_date=data.get('expiration_date'),
            cvv=data.get('cvv'),
        )

        # Create Order Items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                vendor=item.product.vendor,
                quantity=item.quantity,
                price=item.product.price,
            )

        # Clear cart
        cart_items.delete()
        messages.success(request, "✅ Order placed successfully!")
        return redirect('shop:order_success')

    total = request.session.get('checkout_total', 0)
    return render(request, 'shop/payment.html', {'total': total})




def order_success(request):
    return render(request, 'shop/order_success.html')

@login_required(login_url='shop:login')
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        Contact.objects.create(
            name = name,
            email = email,
            subject = subject,
            message = message
        )
        messages.success(request, '✅ Your message has been sent successfully!')
        return redirect('shop:shop_page')
    return render(request,'shop/contact.html')

@login_required(login_url='shop:login')
def vendor_products(request):
    products = Product.objects.filter(
        vendor=request.user,
        status='active',
        is_approved=True
    ).order_by('-created_at')

    return render(request, 'shop/vendor_products.html', {'products': products})

@login_required
def vendor_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)

    if request.method == 'POST':
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.quantity = request.POST['quantity']
        product.status = request.POST['status']
        product.description = request.POST['description']

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        return redirect('shop:vendor_products')

    return render(request, 'shop/vendor_edit.html', {'product': product})

@login_required(login_url='shop:login')
def vendor_orders(request):
    if request.user.user_type != 'vendor':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('shop:login')

    # Only items which belong to this vendor
    order_items = OrderItem.objects.filter(vendor=request.user).order_by('-id')
    return render(request, 'shop/vendor_orders.html', {'order_items': order_items})



@login_required
def orders_view(request):
    orders = Orders.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Orders, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})
