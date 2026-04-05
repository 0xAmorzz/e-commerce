from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from rest_framework_simplejwt.tokens import RefreshToken



class AccountAdapter(DefaultAccountAdapter):
    
    def save_user(self,request,user,form,commit=True):
        user = super().save_user(request,user,form,commit=False)
        if commit:
            user.save()
        return user
    
class SocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        refresh = RefreshToken.for_user(user)
        request.session['access_token'] = str(refresh.access_token)
        request.session['refresh_token'] = str(refresh)
        return user