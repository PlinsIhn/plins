from django.urls import path
from .views import (VendeurSignUpView, MagasinCreateView, VendeurDashboardView, 
                    AjouterProduitView, VendeurProduitView, VendeurProfilView, ProduitDeleteView,
                    MagasinUpdateView, ModifierProduitView
                )
from .views_frais_livraison import (ModeleLivraisonCreateView, ModeleLivraisonListView, ModeleLivraisonUpdateView,
                                    ModeleLivraisonDeleteView, ZoneLivraisonCreateView, ZoneLivraisonUpdateView, ZoneLivraisonDeleteView,
                                    HorsZoneLivraisonCreateView,HorsZoneLivraisonUpdateView, HorsZoneLivraisonDeleteView
                                )
from .api_views import (
                        RegionList, DistrictList, CommuneList, FokontanyList, AdresseIdView  # Vues API
                    )   

urlpatterns = [
    # Vue API REST
    path('api/regions/', RegionList.as_view(), name='api_regions'),
    path('api/districts/', DistrictList.as_view(), name='api_districts'),
    path('api/communes/', CommuneList.as_view(), name='api_communes'),
    path('api/fokontanys/', FokontanyList.as_view(), name='api_fokontanys'),
    path('api/adresse-id/', AdresseIdView.as_view()),

    # Vue CVB
    path('inscription/', VendeurSignUpView.as_view(), name='vendeur_signup'),
    path('magasin/', MagasinCreateView.as_view(), name='vendeur_magasin'),
    path('dashboard/', VendeurDashboardView.as_view(), name='vendeur_dashboard'),
    path('produits/ajouter/', AjouterProduitView.as_view(), name='ajouter_produit'),
    path('produits/modifier/<int:pk>/', ModifierProduitView.as_view(), name='modifier_produit'),

    path('produits/', VendeurProduitView.as_view(), name='produit_vendeur'),
    path('profil/', VendeurProfilView.as_view(), name='vendeur_profil'),
    path('produit/<int:pk>/supprimer/', ProduitDeleteView.as_view(), name='produit_supprimer'),
    path('modifier-magasin/', MagasinUpdateView.as_view(), name='modifier_profil_magasin'),

    # path('frais/modele-livraison/ajout/', ModeleLivraisonCreateView.as_view(), name='ajout_modele_livraison'),
    # urls.py
    path('livraison/modele/ajouter/', ModeleLivraisonCreateView.as_view(), name='ajouter_modele_livraison'),

    path('frais/modele-livraison/liste/', ModeleLivraisonListView.as_view(), name='liste_modele_livraison'),
    path('frais/modele-livraison/<int:pk>/edit/', ModeleLivraisonUpdateView.as_view(), name='edit_modele_livraison'),
    path('frais/modele-livraison/<int:pk>/delete/', ModeleLivraisonDeleteView.as_view(), name='delete_modele_livraison'),
    path('frais/zone-livraison/<int:modele_id>/ajouter-zone/', ZoneLivraisonCreateView.as_view(), name='ajouter_zone_livraison'),
    path('frais/zone-livraison/edit/<int:pk>/', ZoneLivraisonUpdateView.as_view(), name='edit_zone_livraison'),
    path('frais/zone-livraison/<int:pk>/delete/', ZoneLivraisonDeleteView.as_view(), name='delete_zone_livraison'),
    path('frais/horszone-livraison/<int:modele_id>/ajouter/', HorsZoneLivraisonCreateView.as_view(), name='ajouter_horszone_livraison'),
    path('frais/horszone-livraison/<int:pk>/modifier/', HorsZoneLivraisonUpdateView.as_view(), name='edit_horszone_livraison'),
    path('frais/horszone-livraison/<int:pk>/supprimer/', HorsZoneLivraisonDeleteView.as_view(), name='delete_horszone_livraison'),


]