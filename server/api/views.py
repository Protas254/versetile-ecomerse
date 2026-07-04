import os
from django.db import models
import time
import google.generativeai as genai
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, Review, NewsletterSubscriber, Message, Order, OrderItem, UserProfile, FlashSale, Coupon, ReviewImage, ProductImage, Cart
from .serializers import ProductSerializer, ReviewSerializer, UserSerializer, RegisterSerializer, NewsletterSubscriberSerializer, MessageSerializer, OrderSerializer, UserProfileSerializer, FlashSaleSerializer, CouponSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .payments import StripeClient, MpesaClient



class NewsletterSubscribeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = NewsletterSubscriberSerializer(data=request.data)
        if serializer.is_valid():
            subscriber = serializer.save()
            # Send Welcome Email
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                'Welcome to the Eternelle Aura Inner Circle!',
                f'Thank you for subscribing to our newsletter.\n\nYou will be the first to know about our exclusive fragrance launches and special offers.\n\nUse code WELCOME10 for 10% off your next order!',
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=True
            )
            return Response({"message": "Successfully subscribed!"}, status=status.HTTP_201_CREATED)
        # If already subscribed, we can return success too or a specific message
        if 'email' in serializer.errors:
            error_str = str(serializer.errors['email']).lower()
            if 'unique' in error_str or 'exist' in error_str:
                return Response({"message": "You are already subscribed!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Send Welcome Email
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                'Welcome to Eternelle Aura',
                f'Hi {user.first_name or user.username},\n\nWelcome to Eternelle Aura - your home for luxury fragrances. We are excited to have you with us!\n\nExplore our latest collections and find your signature scent today.\n\nHappy Shopping!',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True
            )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add extra responses here
        data['user'] = UserSerializer(self.user).data
        return data

from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardTemplateView(TemplateView):
    template_name = 'admin/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Advanced Sales Analytics'
        return context

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Ideally should be IsAdminUser for write operations
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


    def perform_create(self, serializer):
        product = serializer.save()
        # Handle multiple images if provided in request.FILES
        images = self.request.FILES.getlist('extra_images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        # Handle multiple review photos
        images = self.request.FILES.getlist('review_images')
        for image in images:
            ReviewImage.objects.create(review=review, image=image)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        message = serializer.save()
        # Alert admin
        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            f'New Message from {message.full_name}',
            f'Subject: {message.subject}\n\nMessage:\n{message.message}\n\nReply to: {message.email}',
            settings.DEFAULT_FROM_EMAIL,
            [admin[1] for admin in settings.ADMINS] if hasattr(settings, 'ADMINS') else ['admin@eternelleaura.com'],
            fail_silently=True
        )

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_update(self, serializer):
        old_status = self.get_object().status
        instance = serializer.save()
        new_status = instance.status
        
        if old_status != new_status:
            # Notify customer of status change
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f'Your Eternelle Aura Order #{instance.id} is {new_status}!'
            
            status_messages = {
                'Processing': 'Your order is now being processed by our team and will be ready for shipping soon.',
                'Shipped': 'Great news! Your luxury fragrance is on its way. You can track your order in your account dashboard.',
                'Delivered': 'Your order has been delivered. We hope you love your new scent! Please consider leaving us a review.',
                'Cancelled': 'Your order has been cancelled. If this was a mistake, please contact our support team.',
            }
            
            body = status_messages.get(new_status, f'The status of your order has been updated to: {new_status}')
            
            send_mail(
                subject,
                f'Hi {instance.full_name},\n\n{body}\n\nThank you for choosing Eternelle Aura.',
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=True
            )

    def create(self, request, *args, **kwargs):
        full_name = request.data.get('fullName') or request.data.get('full_name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        shipping_address = request.data.get('shippingAddress') or request.data.get('shipping_address')
        payment_method = request.data.get('paymentMethod') or request.data.get('payment_method', 'Pay After Delivery')
        items_data = request.data.get('items', [])
        coupon_code = request.data.get('couponCode') or request.data.get('coupon_code')
        
        if not items_data:
             return Response({"detail": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

        from django.shortcuts import get_object_or_404
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Mock payment success for "Pay Now"
                # Always start as Pending; callback will update to Paid for Pay Now
                payment_status = 'Pending'
                
                coupon = None
                if coupon_code:
                    coupon = Coupon.objects.filter(code=coupon_code, active=True).first()

                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    shipping_address=shipping_address,
                    payment_method=payment_method,
                    payment_status=payment_status,
                    coupon=coupon,
                    subtotal=0,
                    discount_amount=0,
                    total_price=0 
                )
                
                calculated_total = 0
                for item in items_data:
                    product_id = item.get('product').get('id') if isinstance(item.get('product'), dict) else item.get('product')
                    # Handle both if frontend sends full product obj or just id. 
                    # Ideally frontend sends {product: ID, quantity: N}
                    
                    if not product_id:
                         # Try 'id' if passed inside 'product' key which is not standard but possible
                         pass
                    
                    quantity = item.get('quantity')
                    product = get_object_or_404(Product, id=product_id)
                    
                    if product.stock < quantity:
                        raise ValueError(f"Not enough stock for {product.name}")
                    
                    price = product.price
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price
                    )
                    
                    product.stock -= quantity
                    product.save()
                    
                    calculated_total += price * quantity
                
                order.subtotal = calculated_total
                
                # Apply Coupon Discount
                if coupon:
                    eligible_subtotal = order.subtotal
                    
                    if coupon.target_brand:
                        eligible_subtotal = sum(
                            item.price * item.quantity 
                            for item in OrderItem.objects.filter(order=order, product__brand__iexact=coupon.target_brand)
                        )
                        
                    if eligible_subtotal > 0:
                        if coupon.discount_type == 'Percentage':
                            order.discount_amount = (eligible_subtotal * coupon.value) / 100
                        else:
                            order.discount_amount = min(coupon.value, eligible_subtotal)
                        
                        # Ensure discount doesn't exceed total subtotal just in case
                        if order.discount_amount > order.subtotal:
                            order.discount_amount = order.subtotal
                            
                        coupon.usage_count += 1
                        coupon.save()
                    else:
                        order.discount_amount = 0

                order.total_price = order.subtotal - order.discount_amount

                # Handle installment deposit tracking
                if payment_method == 'Pay in Installments':
                    import math
                    order.deposit_amount = math.ceil(float(order.total_price) * 0.5)
                    order.payment_status = 'Deposit Paid'

                order.save()
                
                # Offload blocking operations to background threads AFTER transaction commit
                import threading
                from django.db import transaction
                
                def post_order_tasks(order_id):
                    try:
                        from django.core.mail import EmailMultiAlternatives
                        from django.template.loader import render_to_string
                        from django.utils.html import strip_tags
                        from django.conf import settings
                        from .models import Order, OrderItem
                        from .utils import check_low_stock
                        import datetime
                        
                        # Now the order is committed and visible to other threads
                        order = Order.objects.get(id=order_id)
                        
                        # 1. Check Low Stock
                        check_low_stock()
                        
                        # 2. Email Logic
                        domain = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
                        year = datetime.datetime.now().year
                        
                        # Prepare context for template
                        context = {
                            'order': order,
                            'domain': domain,
                            'year': year,
                        }
                        
                        html_content = render_to_string('emails/order_confirmation.html', context)
                        text_content = strip_tags(html_content)
                        
                        # Notify Customer
                        msg = EmailMultiAlternatives(
                            'Eternelle Aura - Order Confirmation',
                            text_content,
                            settings.DEFAULT_FROM_EMAIL,
                            [order.email]
                        )
                        msg.attach_alternative(html_content, "text/html")
                        msg.send(fail_silently=False)
                        
                        # ALERT ADMIN
                        send_mail(
                            f'NEW ORDER: Order #{order.id}',
                            f'New order by {order.full_name} ({order.email}).\nTotal: KSh {order.total_price}',
                            settings.DEFAULT_FROM_EMAIL,
                            [admin[1] for admin in settings.ADMINS] if hasattr(settings, 'ADMINS') else ['admin@eternelleaura.com'],
                            fail_silently=False,
                        )
                    except Exception as e:
                        import traceback
                        print(f"Background tasks failed for Order #{order_id}: {str(e)}")
                        traceback.print_exc()

                transaction.on_commit(lambda: threading.Thread(target=post_order_tasks, args=(order.id,)).start())

                serializer = self.get_serializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        name = request.data.get('name')
        phone = request.data.get('phone')
        
        if name:
            user.first_name = name
            user.save()
            
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if phone is not None:
            profile.phone = phone
            profile.save()
            
        return Response(UserSerializer(user).data)

class ChatBotAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_message = request.data.get('message', '')
        history = request.data.get('history', [])
        
        if not user_message:
            return Response({"response": "I didn't receive a message. How can I help?"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Configure Gemini
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            # Fallback to smart local logic if no API key is present
            msg_lower = user_message.lower()
            response_text = ""
            
            if any(word in msg_lower for word in ['hello', 'hi', 'hey', 'greetings']):
                response_text = "Hello! I'm currently in a limited offline mode, but I can still help you find some amazing fragrances. What kind of scent are you looking for?"
            elif any(word in msg_lower for word in ['price', 'cost', 'how much']):
                response_text = "Our luxury perfumes vary in price. You can find our full collection and pricing on our Shop page. We also offer free shipping on orders over KSh 5000!"
            elif any(word in msg_lower for word in ['delivery', 'shipping']):
                response_text = "We offer delivery nationwide! Delivery timelines and fees depend on your location. Free shipping is available for orders over KSh 5000."
            elif any(word in msg_lower for word in ['recommend', 'best', 'popular', 'perfume', 'scent']):
                products = Product.objects.all()[:3]
                if products.exists():
                    names = [p.name for p in products]
                    response_text = f"I'd highly recommend checking out some of our favorites: {', '.join(names)}. They are absolutely exquisite!"
                else:
                    response_text = "We have a wonderful selection of fragrances in our store. Please browse our Shop to see the latest collection!"
            else:
                response_text = "I'm currently operating in a limited offline mode, so I might not fully understand. Feel free to browse our shop or contact support if you need detailed assistance!"
            
            return Response({"response": response_text, "status": "offline_mode"}, status=status.HTTP_200_OK)

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prepare context about the store
            store_context = "You are an AI assistant for 'Eternelle Aura', a luxury perfume store in Kenya. "
            products = Product.objects.all()
            if products.exists():
                store_context += "Our current products include: " + ", ".join([f"{p.name} (KSh {p.price})" for p in products[:10]])
            
            prompt = f"{store_context}\n\nCustomer: {user_message}\nAI:"
            
            response = model.generate_content(prompt)
            return Response({"response": response.text, "status": "success"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Gemini Error: {e}")
            return Response({"response": "I'm having trouble thinking clearly right now. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            frontend_url = request.META.get('HTTP_ORIGIN', 'http://localhost:5173')
            reset_url = f"{frontend_url}/reset-password?uid={uid}&token={token}"
            
            send_mail(
                'Reset Your Password - Eternelle Aura',
                f'Click the link to reset your password: {reset_url}',
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@eternelleaura.com'),
                [email],
                fail_silently=True,
            )
        except Exception:
            pass # Keep silent for security
        return Response({'message': 'If an account exists, a reset link was sent.'})

class CartSyncView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items = request.data.get('items', [])
        cart.save()
        return Response({"status": "success"})

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response({"items": cart.items})

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('password')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Password reset successful'})
            else:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

class FlashSaleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FlashSale.objects.filter(is_active=True).order_by('-end_time')
    serializer_class = FlashSaleSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        # We only want the most recent active flash sale for simplicity
        active_sale = self.get_queryset().first()
        if active_sale:
            serializer = self.get_serializer(active_sale)
            return Response(serializer.data)
        return Response({}, status=status.HTTP_200_OK)

class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Coupon.objects.filter(active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        # We use 'code' as the lookup field
        code = kwargs.get('pk')
        coupon = Coupon.objects.filter(code=code, active=True).first()
        if not coupon:
             return Response({"detail": "Invalid or expired coupon"}, status=status.HTTP_404_NOT_FOUND)
        
        from django.utils import timezone
        if coupon.expiry_date and coupon.expiry_date < timezone.now():
            return Response({"detail": "Coupon has expired"}, status=status.HTTP_400_BAD_REQUEST)
            
        if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
            return Response({"detail": "Coupon usage limit reached"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(coupon)
        return Response(serializer.data)

class AdminAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from django.db.models import Sum, Count
        from django.db.models.functions import TruncDate
        
        # Sales over time
        sales_data = Order.objects.filter(payment_status='Paid').annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total_price'),
            orders=Count('id')
        ).order_by('date')
        
        # Top products
        top_products = OrderItem.objects.filter(order__payment_status='Paid').values(
            'product__name'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_sold')[:5]
        
        # Stock alerts
        low_stock = Product.objects.filter(stock__lte=models.F('low_stock_threshold')).values('name', 'stock')

        # Abandoned carts (last 24 hours, non-empty, and user has no recent order)
        from django.utils import timezone
        from datetime import timedelta
        yesterday = timezone.now() - timedelta(hours=24)
        abandoned_carts = Cart.objects.filter(updated_at__gte=yesterday).exclude(items=[])
        
        # Further refine: exclude users who placed an order in the last 24h
        recent_order_users = Order.objects.filter(created_at__gte=yesterday).values_list('user', flat=True)
        abandoned_carts = abandoned_carts.exclude(user__id__in=recent_order_users).values('user__username', 'user__email', 'updated_at', 'items')

        return Response({
            "sales": list(sales_data),
            "topProducts": list(top_products),
            "lowStock": list(low_stock),
            "abandonedCarts": list(abandoned_carts)
        })

class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        stripe_client = StripeClient()
        intent = stripe_client.create_payment_intent(float(amount))
        
        if "error" in intent:
            return Response(intent, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(intent)

class MpesaStkPushView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        phone = request.data.get('phone')
        amount = request.data.get('amount')
        order_id = request.data.get('order_id')
        
        if not all([phone, amount, order_id]):
            return Response({"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Format phone to 2547XXXXXXXX
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]
            
        mpesa = MpesaClient()
        response = mpesa.stk_push(
            phone=phone,
            amount=amount,
            reference=f"ORDER{order_id}",
            description=f"Payment for Order #{order_id}"
        )
        
        # Save MerchantRequestID for callback tracking
        if "MerchantRequestID" in response:
            try:
                order = Order.objects.get(id=order_id)
                order.payment_reference = response["MerchantRequestID"]
                order.save()
            except Order.DoesNotExist:
                pass
                
        return Response(response)

class MpesaCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Handle M-Pesa STK Push results."""
        data = request.data
        body = data.get('Body', {}).get('stkCallback', {})
        result_code = body.get('ResultCode')
        merchant_request_id = body.get('MerchantRequestID')
        
        print(f"M-Pesa Callback Received: {result_code} for {merchant_request_id}")
        
        try:
            order = Order.objects.get(payment_reference=merchant_request_id)
            if result_code == 0:
                # Payment Successful
                order.payment_status = 'Paid'
                order.save()
                # Additional logic like sending confirmation email could go here
            else:
                # Payment Failed or Cancelled
                order.payment_status = 'Failed'
                order.save()
        except Order.DoesNotExist:
            print(f"Order with reference {merchant_request_id} not found")
            
        return Response({"ResultCode": 0, "ResultDesc": "Success"})
