from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, View
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from .forms import RegistrationForm
from myapp.models import UserProfile


class RegisterView(FormView):
    template_name = 'accounts/signup.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('verification-sent')

    def dispatch(self, request, *args, **kwargs):
        # If already logged in, redirect to home
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Save user but set inactive until email verified
        user = form.save(commit=False)
        user.is_active = False  # User cannot login until verified
        user.save()
        
        # Create user profile for verification
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.verification_sent_at = timezone.now()
        profile.save()
        
        # Send verification email
        verification_url = self.request.build_absolute_uri(
            f'/accounts/verify/{profile.verification_token}/'
        )
        
        try:
            send_mail(
                subject='Verify Your Email - Blog Platform',
                message=f'''Hi {user.username},

Welcome to our Blog Platform! Please verify your email address to activate your account.

Click the link below to verify (expires in 1 hour):
{verification_url}

If you didn't create this account, please ignore this email.

Best regards,
The Blog Team''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(
                self.request, 
                f'Account created! Please check your email ({user.email}) to verify your account.'
            )
        except Exception as e:
            # If email fails, still show success but log error
            messages.warning(
                self.request,
                'Account created but verification email failed to send. Please contact support.'
            )
        
        return super().form_valid(form)


class VerificationSentView(TemplateView):
    """Page shown after signup"""
    template_name = 'accounts/verification_sent.html'


class VerifyEmailView(View):
    """Handle email verification link clicks"""
    
    def get(self, request, token):
        try:
            profile = get_object_or_404(UserProfile, verification_token=token)
            
            # Check if already verified
            if profile.email_verified:
                messages.info(request, 'Your email is already verified. You can login now.')
                return redirect('login')
            
            # Check if token expired
            if profile.is_verification_expired():
                messages.error(
                    request,
                    'Verification link has expired (1 hour limit). Please request a new one.'
                )
                return redirect('resend-verification')
            
            # Verify the email
            profile.email_verified = True
            profile.save()
            
            # Activate the user account
            user = profile.user
            user.is_active = True
            user.save()
            
            # Send success email
            try:
                send_mail(
                    subject='Email Verified Successfully!',
                    message=f'''Hi {user.username},

Your email has been verified successfully! Your account is now active.

You can now login and start using our blog platform:
{request.build_absolute_uri('/accounts/login/')}

Best regards,
The Blog Team''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except:
                pass  # Don't fail if confirmation email doesn't send
            
            messages.success(
                request,
                'Email verified successfully! You can now login to your account.'
            )
            return redirect('login')
            
        except UserProfile.DoesNotExist:
            messages.error(request, 'Invalid verification link.')
            return redirect('login')


class ResendVerificationView(TemplateView):
    """View to resend verification email"""
    template_name = 'accounts/resend_verification.html'
    
    def post(self, request):
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email, is_active=False)
            profile = user.profile
            
            # Check if already verified
            if profile.email_verified:
                messages.info(request, 'This email is already verified.')
                return redirect('login')
            
            # Generate new token and update timestamp
            import uuid
            profile.verification_token = uuid.uuid4()
            profile.verification_sent_at = timezone.now()
            profile.save()
            
            # Send new verification email
            verification_url = request.build_absolute_uri(
                f'/accounts/verify/{profile.verification_token}/'
            )
            
            send_mail(
                subject='Verify Your Email - Blog Platform',
                message=f'''Hi {user.username},

Here is your new verification link (expires in 1 hour):
{verification_url}

Best regards,
The Blog Team''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            messages.success(
                request,
                f'Verification email has been resent to {email}. Please check your inbox.'
            )
            return redirect('verification-sent')
            
        except User.DoesNotExist:
            messages.error(request, 'No unverified account found with this email.')
            return redirect('resend-verification')
        except Exception as e:
            messages.error(request, 'Failed to send verification email. Please try again later.')
            return redirect('resend-verification')
