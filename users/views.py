from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import LoginForm
from vendeur.models import Magasin

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        next_url = request.GET.get('next', '')
        return render(request, 'users/login.html', {'form': form, 'next': next_url})

    def post(self, request):
        form = LoginForm(request.POST)
        next_url = request.POST.get('next')

        if form.is_valid():
            user = form.cleaned_data["user"]
            if user.role != 'vendeur':
                form.add_error(None, "Numéro ou mot de passe incorrect")
                return render(request, 'users/login.html', {'form': form})

            login(request, user)

            if next_url and next_url.startswith('/'):
                return redirect(next_url)

            if not user.is_active:
                try:
                    user.magasin
                    return redirect('vendeur_dashboard')
                except (Magasin.DoesNotExist, AttributeError):
                    return redirect('vendeur_magasin')
            else:
                return redirect('vendeur_dashboard')

        return render(request, 'users/login.html', {'form': form})



class LoginAcheteurView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'users/login_acheteur.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            if user.role != 'acheteur':
                form.add_error(None, "Numéro ou mot de passe incorrect")
                return render(request, 'users/login_acheteur.html', {'form': form})

            login(request, user)
            return redirect('profil_acheteur')

        return render(request, 'users/login_acheteur.html', {'form': form})
    


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login_vendeur')  # ou autre nom de route

def logout_acheteur_view(request):
    logout(request)
    return redirect('login_acheteur')  # nom de l'URL login acheteur


# users/views.py
from django.shortcuts import redirect

def redirect_after_login(request):
    user = request.user
    if user.role == 'vendeur':
        return redirect('vendeur_dashboard')
    elif user.role == 'acheteur':
        return redirect('acheteur_profil')

