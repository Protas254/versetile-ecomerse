from rest_framework import serializers
from .models import Product, Review, NewsletterSubscriber, Message, Order, OrderItem, UserProfile, FlashSale, ProductImage, ReviewImage, Coupon
from django.contrib.auth.models import User



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone']

class UserSerializer(serializers.ModelSerializer):
    isAdmin = serializers.BooleanField(source='is_staff', read_only=True)
    name = serializers.SerializerMethodField()
    phone = serializers.CharField(source='profile.phone', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'isAdmin', 'phone']

    def get_name(self, obj):
        return obj.first_name if obj.first_name else obj.username

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'phone')

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)
        user = User.objects.create_user(
            username=validated_data['email'], # Use email as username
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('name', '')
        )
        if phone:
            UserProfile.objects.create(user=user, phone=phone)
        return user

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image']

class ReviewSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.username', read_only=True)
    userId = serializers.CharField(source='user.id', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'userId', 'userName', 'rating', 'comment', 'images', 'date']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

class ProductSerializer(serializers.ModelSerializer):
    scentType = serializers.CharField(source='scent_type')
    fragranceNotes = serializers.JSONField(source='fragrance_notes')
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    images = ProductImageSerializer(many=True, read_only=True)
    lowStockThreshold = serializers.IntegerField(source='low_stock_threshold', read_only=True)
    discountPrice = serializers.DecimalField(source='discount_price', max_digits=10, decimal_places=2, required=False, allow_null=True)

    def to_internal_value(self, data):
        # Handle fragranceNotes if it comes as a JSON string (from FormData)
        if 'fragranceNotes' in data:
            import json
            # Convert QueryDict to a regular dict to ensure our modifications are preserved correctly
            if hasattr(data, 'dict'):
                data = data.dict()
            elif hasattr(data, 'copy'):
                data = data.copy()
            else:
                data = dict(data)
                
            val = data.get('fragranceNotes')
            if isinstance(val, str):
                try:
                    data['fragranceNotes'] = json.loads(val)
                except (json.JSONDecodeError, ValueError):
                    raise serializers.ValidationError({'fragranceNotes': 'Invalid JSON format'})
        return super().to_internal_value(data)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'price', 'discountPrice', 'image', 'images', 'description', 'scentType', 'gender',
                  'fragranceNotes', 'rating', 'reviews', 'stock', 'lowStockThreshold', 'featured']

class CouponSerializer(serializers.ModelSerializer):
    discountType = serializers.CharField(source='discount_type')
    expiryDate = serializers.DateTimeField(source='expiry_date', required=False, allow_null=True)
    minPurchase = serializers.DecimalField(source='min_purchase', max_digits=10, decimal_places=2)

    targetBrand = serializers.CharField(source='target_brand', required=False, allow_null=True)

    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discountType', 'value', 'minPurchase', 'active', 'expiryDate', 'targetBrand']

class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']

class MessageSerializer(serializers.ModelSerializer):
    isReplied = serializers.BooleanField(source='is_replied', read_only=True)
    replyMessage = serializers.CharField(source='reply_message', required=False, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    fullName = serializers.CharField(source='full_name')

    class Meta:
        model = Message
        fields = ['id', 'fullName', 'email', 'subject', 'message', 'isReplied', 'replyMessage', 'createdAt']

class OrderItemSerializer(serializers.ModelSerializer):
    productName = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'productName', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    userName = serializers.CharField(source='user.username', read_only=True)
    userEmail = serializers.CharField(source='user.email', read_only=True)

    fullName = serializers.CharField(source='full_name')
    paymentMethod = serializers.CharField(source='payment_method')
    paymentStatus = serializers.CharField(source='payment_status', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    totalPrice = serializers.DecimalField(source='total_price', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discountAmount = serializers.DecimalField(source='discount_amount', max_digits=10, decimal_places=2, read_only=True)
    couponCode = serializers.CharField(source='coupon.code', read_only=True)
    shippingAddress = serializers.CharField(source='shipping_address')

    depositAmount = serializers.DecimalField(source='deposit_amount', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'userName', 'userEmail', 'fullName', 'phone', 'items', 
                  'subtotal', 'couponCode', 'discountAmount', 'totalPrice', 'shippingAddress', 
                  'paymentMethod', 'paymentStatus', 'depositAmount', 'status', 'createdAt']

class FlashSaleSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    endTime = serializers.DateTimeField(source='end_time')
    discountPercentage = serializers.IntegerField(source='discount_percentage')

    class Meta:
        model = FlashSale
        fields = ['id', 'name', 'endTime', 'products', 'is_active', 'discountPercentage']
