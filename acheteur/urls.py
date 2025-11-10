from django.urls import path
from .views import  ( ListeProduitsView,ProduitDetailPublicView, SignupAcheteurView, ProfilAcheteurView, 
                        AjouterAdresseAcheteurView, ListeAdressesAcheteurView, SupprimerAdresseAcheteurView, ModifierAdresseAcheteurView,
                        RechercheProduitView, ProduitsMagasinView, RechercheProduitsMagasinView
                    )

urlpatterns = [
    path ('', ListeProduitsView.as_view(), name='liste_produits'),
    path('inscription/', SignupAcheteurView.as_view(), name='signup_acheteur'),
    path('produits/<int:produit_id>/', ProduitDetailPublicView.as_view(), name='acheteur_detail_produit'),
    path('profil/', ProfilAcheteurView.as_view(), name='profil_acheteur'),
    path('ajouter-adresse/', AjouterAdresseAcheteurView.as_view(), name='ajouter_adresse'),
    path('modifier-adresse/<int:pk>/', ModifierAdresseAcheteurView.as_view(), name='modifier_adresse'),
    path('liste_adresses/', ListeAdressesAcheteurView.as_view(), name='liste_adresses'),
    path('adresse/supprimer/<int:pk>/', SupprimerAdresseAcheteurView.as_view(), name='supprimer_adresse'),

    path('recherche/', RechercheProduitView.as_view(), name='acheteur_recherche_produit'),
    path('magasin/<int:magasin_id>/', ProduitsMagasinView.as_view(), name='acheteur_produits_magasin'),
    path("magasin/<int:magasin_id>/recherche/", RechercheProduitsMagasinView.as_view(), name="acheteur_recherche_produits_magasin")
]
