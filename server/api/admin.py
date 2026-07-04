from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Product, Review, Message, NewsletterSubscriber, Order, OrderItem, 
    UserProfile, Customer, FlashSale, Coupon, Cart, ProductImage, ReviewImage
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'scent_type', 'stock', 'low_stock_threshold', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('scent_type', 'created_at')
    list_editable = ('stock', 'low_stock_threshold')
    inlines = [ProductImageInline]

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'date')
    list_filter = ('rating', 'date')
    inlines = [ReviewImageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'is_replied', 'created_at')
    list_filter = ('is_replied', 'created_at')
    search_fields = ('full_name', 'email', 'subject', 'message')

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'subtotal', 'discount_amount', 'total_price', 'payment_status', 'status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'id')
    inlines = [OrderItemInline]
    list_editable = ('status', 'payment_status')
    readonly_fields = ('subtotal', 'discount_amount', 'total_price')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'active', 'usage_count', 'expiry_date')
    list_filter = ('active', 'discount_type')
    search_fields = ('code',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    search_fields = ('user__username', 'user__email')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_phone', 'date_joined', 'is_active')
    search_fields = ('username', 'email', 'profile__phone', 'first_name', 'last_name')
    list_filter = ('is_active', 'date_joined')
    ordering = ('-date_joined',)

    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, 'profile') else None
    get_phone.short_description = 'Phone'

    def get_queryset(self, request):
        # Optionally filter out staff if you want "Customers" to strictly be non-admins
        return super().get_queryset(request).filter(is_staff=False)

@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'end_time', 'is_active', 'discount_percentage')
    list_filter = ('is_active',)
    filter_horizontal = ('products',)
