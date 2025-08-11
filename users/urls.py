from django.urls import path
from .views import LoginView, logout_view, LoginAcheteurView, logout_acheteur_view

urlpatterns = [
    path('vendeur/login/', LoginView.as_view(), name='login_vendeur'),
    path('acheteur/login/', LoginAcheteurView.as_view(), name='login_acheteur'),
    path('logout/', logout_view, name='logout'),
    path('acheteur/logout/', logout_acheteur_view, name='logout_acheteur')
]
