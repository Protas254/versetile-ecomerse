from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    SCENT_TYPES = [
        ('Floral', 'Floral'),
        ('Woody', 'Woody'),
        ('Oriental', 'Oriental'),
        ('Fresh', 'Fresh'),
        ('Citrus', 'Citrus'),
        ('Spicy', 'Spicy'),
    ]

    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=200, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField()
    scent_type = models.CharField(max_length=50, choices=SCENT_TYPES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Unisex')
    fragrance_notes = models.JSONField(default=dict)
    stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            from PIL import Image
            import os
            
            # Open the image using Pillow
            img_path = self.image.path
            img = Image.open(img_path)
            
            # If it's already WebP, do nothing
            if img.format == 'WEBP':
                return
                
            # Convert to WebP
            webp_path = os.path.splitext(img_path)[0] + '.webp'
            img.save(webp_path, 'WEBP', quality=80)
            
            # Update the image field to point to the new webp file
            old_path = self.image.name
            new_path = os.path.splitext(old_path)[0] + '.webp'
            
            # Update field without triggering another save
            Product.objects.filter(id=self.id).update(image=new_path)
            
            # Clean up the old file if it was different
            if img_path != webp_path and os.path.exists(img_path):
                os.remove(img_path)

    def __str__(self):
        return self.name
    
    @property
    def rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='reviews/')

    def __str__(self):
        return f"Image for review by {self.review.user.username}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Message(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_replied = models.BooleanField(default=False)
    reply_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('Percentage', 'Percentage'),
        ('Fixed', 'Fixed'),
    ]
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='Percentage')
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    target_brand = models.CharField(max_length=200, blank=True, null=True, help_text="If set, coupon only applies to products of this brand")
    expiry_date = models.DateTimeField(blank=True, null=True)
    usage_limit = models.IntegerField(default=None, blank=True, null=True)
    usage_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.code} ({self.value} {self.discount_type})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('Pay Now', 'Pay Now'),
        ('Pay After Delivery', 'Pay After Delivery'),
        ('Pay in Installments', 'Pay in Installments'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Deposit Paid', 'Deposit Paid'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, default="")
    email = models.EmailField(default="")
    phone = models.CharField(max_length=20, default="")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='Pay After Delivery')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # For installment orders
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_reference = models.CharField(max_length=100, blank=True, null=True) # M-Pesa MerchantRequestID or Stripe ID
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Customer(User):
    class Meta:
        proxy = True
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ('-date_joined',)

class FlashSale(models.Model):
    name = models.CharField(max_length=200, default="Flash Sale")
    end_time = models.DateTimeField()
    products = models.ManyToManyField(Product, related_name='flash_sales')
    is_active = models.BooleanField(default=True)
    discount_percentage = models.IntegerField(default=0, help_text="Informational discount percentage to show")

    def __str__(self):
        return f"{self.name} - Ends at {self.end_time}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    items = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"
