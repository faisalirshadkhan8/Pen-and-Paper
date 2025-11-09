from django.urls import path
from .views import RegisterView, VerificationSentView, VerifyEmailView, ResendVerificationView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('verification-sent/', VerificationSentView.as_view(), name='verification-sent'),
    path('verify/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
]
