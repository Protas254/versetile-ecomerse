from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Cart, Order
from django.utils import timezone
from datetime import timedelta

def check_low_stock():
    """Checks for products with stock below threshold and sends alerts."""
    low_stock_products = Product.objects.filter(stock__lte=models.F('low_stock_threshold'))
    
    if low_stock_products.exists():
        message = "The following products are low on stock:\n\n"
        for product in low_stock_products:
            message += f"- {product.name}: {product.stock} left (Threshold: {product.low_stock_threshold})\n"
        
        send_mail(
            'URGENT: Low Stock Alert - Eternelle Aura',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin[1] for admin in settings.ADMINS] if hasattr(settings, 'ADMINS') else ['admin@eternelleaura.com'],
            fail_silently=True
        )
        return len(low_stock_products)
    return 0

def send_abandoned_cart_emails():
    """Finds abandoned carts and sends recovery emails."""
    yesterday = timezone.now() - timedelta(hours=24)
    # Get carts updated in last 24h that aren't empty
    abandoned_carts = Cart.objects.filter(updated_at__gte=yesterday).exclude(items=[])
    
    # Exclude users who placed an order recently
    recent_order_users = Order.objects.filter(created_at__gte=yesterday).values_list('user', flat=True)
    abandoned_carts = abandoned_carts.exclude(user__id__in=recent_order_users)
    
    count = 0
    for cart in abandoned_carts:
        try:
            send_mail(
                'Are you still interested? - Eternelle Aura',
                f'Hi {cart.user.first_name or cart.user.username},\n\nWe noticed you left some luxury items in your cart. '
                f'Complete your purchase now and use code EURA10 for 10% OFF!\n\nShop here: https://eternelleaura.com/cart',
                settings.DEFAULT_FROM_EMAIL,
                [cart.user.email],
                fail_silently=True
            )
            count += 1
        except Exception:
            continue
    return count
