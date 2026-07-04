from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, ReviewViewSet, CustomTokenObtainPairView, RegisterView, 
    NewsletterSubscribeView, MessageViewSet, OrderViewSet, ChatBotAPIView, 
    ProfileUpdateView, PasswordResetRequestView, PasswordResetConfirmView, 
    FlashSaleViewSet, CouponViewSet, AdminAnalyticsView, CartSyncView, AdminDashboardTemplateView,
    CreatePaymentIntentView, MpesaStkPushView, MpesaCallbackView
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'flash-sale', FlashSaleViewSet, basename='flashsale')
router.register(r'coupons', CouponViewSet, basename='coupon')


urlpatterns = [
    path('', include(router.urls)),
    path('chat/', ChatBotAPIView.as_view(), name='chatbot_api'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/profile/', ProfileUpdateView.as_view(), name='update_profile'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/newsletter/', NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/analytics/', AdminAnalyticsView.as_view(), name='admin_analytics'),
    path('admin/analytics-view/', AdminDashboardTemplateView.as_view(), name='admin_analytics_view'),
    path('cart/sync/', CartSyncView.as_view(), name='cart_sync'),
    
    # Payments
    path('payments/stripe/intent/', CreatePaymentIntentView.as_view(), name='stripe_intent'),
    path('payments/mpesa/stkpush/', MpesaStkPushView.as_view(), name='mpesa_stkpush'),
    path('payments/mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa_callback'),
]
