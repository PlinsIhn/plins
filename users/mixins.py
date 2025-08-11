# users/mixins.py
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

class VendeurRequiredMixin(LoginRequiredMixin):
    login_url = '/users/vendeur/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'vendeur':
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

class AcheteurRequiredMixin(LoginRequiredMixin):
    login_url = '/users/acheteur/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'acheteur':
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
