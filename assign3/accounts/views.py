from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages
from django.shortcuts import redirect

from .forms import RegistrationForm


class RegisterView(FormView):
    template_name = 'accounts/signup.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        # If already logged in, redirect to home
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Welcome, {user.username}! Your account has been created.')
        return super().form_valid(form)
