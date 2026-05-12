from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import User


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        valid_types = {choice[0] for choice in User.UserType.choices}
        selected = request.session.pop('selected_user_type', None)
        if selected in valid_types:
            user.user_type = selected
        else:
            user.user_type = User.UserType.STUDENT
        user.save(update_fields=['user_type'])
        return user

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email')
        if email and not sociallogin.is_existing:
            try:
                existing = User.objects.get(email=email)
                sociallogin.connect(request, existing)
            except User.DoesNotExist:
                pass
