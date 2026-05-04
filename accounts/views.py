from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import UserRegistrationForm, EmailAuthenticationForm, EmailPasswordResetForm, CustomSetPasswordForm

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('screen1')

    def form_valid(self, form):
        user = form.save()
        auth_login(self.request, user)
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        user_type = self.request.GET.get('type') or self.request.session.get('selected_user_type')
        if user_type:
            initial['user_type'] = user_type
        return initial

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    # Added extra redirect before lazy dashboard/main homepage redirect, in-case user was trying to access 
    # a specific page before logging in.
    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_type = self.request.GET.get('type')
        if user_type:
            self.request.session['selected_user_type'] = user_type
        context['selected_user_type'] = user_type
        return context


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.txt'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    form_class = EmailPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    form_class = CustomSetPasswordForm
