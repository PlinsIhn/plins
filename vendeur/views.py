from django.views import View
from django.shortcuts import render, redirect
from .forms import VendeurSignUpForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import MagasinForm
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView
from .forms import ProduitForm

from .models import Produits
from .models import Magasin
from django.urls import reverse

class VendeurSignUpView(View):
    def get(self, request):
        form = VendeurSignUpForm()
        return render(request, 'vendeur/signup.html', {'form': form})

    def post(self, request):
        form = VendeurSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vendeur_magasin')  # à remplacer plus tard par ta vraie page de connexion
        return render(request, 'vendeur/signup.html', {'form': form})

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import MagasinForm
from .models import Adresse, Magasin
from django.core.exceptions import ObjectDoesNotExist

class MagasinCreateView(LoginRequiredMixin, View):
    login_url = '/users/vendeur/login/'

    def get(self, request):
        user = request.user
        try:
            _ = user.magasin
            return redirect('vendeur_dashboard')
        except ObjectDoesNotExist:
            pass

        form = MagasinForm()
        return render(request, 'vendeur/magasin_form.html', {'form': form})

    def post(self, request):
        user = request.user
        try:
            _ = user.magasin
            return redirect('vendeur_dashboard')
        except ObjectDoesNotExist:
            pass

        form = MagasinForm(request.POST, request.FILES)
        adresse_id = request.POST.get("adresse_magasin")

        if form.is_valid() and adresse_id:
            magasin = form.save(commit=False)
            magasin.vendeur = user
            try:
                magasin.adresse_magasin = Adresse.objects.get(id=adresse_id)
            except Adresse.DoesNotExist:
                magasin.adresse_magasin = None

            magasin.save()
            return redirect('vendeur_dashboard')

        return render(request, 'vendeur/magasin_form.html', {'form': form})



from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.forms import inlineformset_factory

from .models import Produits, VariationProduit, DetailleProduit, ModeleLivraison
from .forms import ProduitForm, VariationProduitForm, DetailleProduitForm
from django.contrib import messages
from .utils import compress_image, compresser_video

# Formsets
VariationProduitFormSet = inlineformset_factory(
    Produits,
    VariationProduit,
    form=VariationProduitForm,
    extra=1,
    can_delete=True
)

DetailleProduitFormSet = inlineformset_factory(
    Produits,
    DetailleProduit,
    form=DetailleProduitForm,
    extra=1,
    can_delete=True
)
import tempfile
import subprocess
import json
import os
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import JsonResponse

def flatten_errors(errors):
    flat_list = []
    for index, form_errors in enumerate(errors, start=1):
        for field, messages in form_errors.items():
            for msg in messages:
                flat_list.append(f"Variation {index} - {field} : {msg}")
    return flat_list


class AjouterProduitView(LoginRequiredMixin, View):
    login_url = '/users/vendeur/login/'

    def dispatch(self, request, *args, **kwargs):
        # Vérifie si l'utilisateur a un magasin
        try:
            magasin = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')

        # Vérifie si un modèle de livraison existe
        modele = ModeleLivraison.objects.filter(magasin=magasin).first()
        if not modele:
            messages.error(request, "Vous devez d'abord configurer votre modèle de livraison.")
            return redirect('liste_modele_livraison')

        zones_count = modele.zones.count()
        horszones_count = modele.horszones.count()

        if zones_count == 0 and horszones_count == 0:
            messages.error(request, "Mampidira Zone de livraison")
            return redirect('liste_modele_livraison')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        produit_form = ProduitForm()
        variation_formset = VariationProduitFormSet()
        detaille_formset = DetailleProduitFormSet()
        return render(request, 'vendeur/ajouter_produit.html', {
            'produit_form': produit_form,
            'variation_formset':variation_formset,
            
        })

    def post(self, request):
        produit_form = ProduitForm(request.POST, request.FILES)

        if not produit_form.is_valid():
            return JsonResponse({
                'errors': {
                    'form_errors': produit_form.errors
                }
            }, status=400)

        # On sauvegarde le produit d'abord
        produit = produit_form.save(commit=False)
        produit.magasin = request.user.magasin
        produit.save()

        # IMPORTANT : on passe instance=produit pour lier le formset
        variation_formset = VariationProduitFormSet(request.POST, request.FILES, instance=produit)

        if not variation_formset.is_valid():
            return JsonResponse({
                'errors': {
                    'formset_errors': flatten_errors(variation_formset.errors)
                }
            }, status=400)

        # Vérification qu'au moins une variation valide existe
        has_valid_variation = any(
            form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            for form in variation_formset
        )
        if not has_valid_variation:
            return JsonResponse({
                'errors': {
                    'formset_errors': ['Veuillez ajouter au moins une variation.']
                }
            }, status=400)

        variation_formset.save()

        # Gestion des images
        detaille_images = request.FILES.getlist('detaille_image')
        nb_existantes = DetailleProduit.objects.filter(detaille_produit=produit).count()
        nb_nouvelles = len(detaille_images)

        if nb_existantes + nb_nouvelles > 10:
            return JsonResponse({
                'errors': {
                    'form_errors': {'detaille_image': ["Maximum 10 images autorisées."]}
                }
            }, status=400)

        for image in detaille_images:
            image_compressée = compress_image(image)
            DetailleProduit.objects.create(
                detaille_produit=produit,
                detaille_image=image_compressée
            )

        # Gestion de la vidéo
        detaille_file = request.FILES.get('detaille_file')
        if detaille_file and detaille_file.content_type.startswith('video'):
            video_compressée = compresser_video(detaille_file)
            DetailleProduit.objects.create(
                detaille_produit=produit,
                detaille_file=video_compressée
            )

        return JsonResponse({'message': 'Produit ajouté avec succès !'}, status=200)




class ModifierProduitView(LoginRequiredMixin, View):
    login_url = '/users/vendeur/login/'

    def dispatch(self, request, *args, **kwargs):
        # Vérifie si l'utilisateur a un magasin
        try:
            magasin = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')

        # Vérifie si un modèle de livraison existe
        modele = ModeleLivraison.objects.filter(magasin=magasin).first()
        if not modele:
            messages.error(request, "Vous devez d'abord configurer votre modèle de livraison.")
            return redirect('liste_modele_livraison')

        zones_count = modele.zones.count()
        horszones_count = modele.horszones.count()

        if zones_count == 0 and horszones_count == 0:
            messages.error(request, "Mampidira Zone de livraison")
            return redirect('liste_modele_livraison')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        produit = get_object_or_404(Produits, pk=pk, magasin=request.user.magasin)

        produit_form = ProduitForm(instance=produit)
        variation_formset = VariationProduitFormSet(instance=produit)
        detaille = produit.detailleproduit.all()

        has_existing_image = any(d.detaille_image for d in detaille)
        has_existing_video = any(d.detaille_file for d in detaille)


        return render(request, 'vendeur/modifier_produit.html', {
            'produit_form': produit_form,
            'variation_formset': variation_formset,
            'produit': produit,
            'detaille':detaille,
            'has_existing_image': has_existing_image,
            'has_existing_video': has_existing_video,
        })
    
    def post(self, request, pk):
        
        produit = get_object_or_404(Produits, pk=pk, magasin=request.user.magasin)        
        produit_form = ProduitForm(request.POST, request.FILES, instance=produit)
        variation_formset = VariationProduitFormSet(request.POST, request.FILES, instance=produit)
        detaille = produit.detailleproduit.all()
        
        detaille_images = request.FILES.getlist('detaille_image')
        detaille_file = request.FILES.get('detaille_file')

        if all([produit_form.is_valid(), variation_formset.is_valid()]):
            has_valid_variation = any(
                form.cleaned_data and not form.cleaned_data.get('DELETE', False)
                for form in variation_formset
            )

            if not has_valid_variation:
                return JsonResponse({
                    'errors': {
                        'variation_formset_errors': ['Veuillez ajouter au moins une variation.']
                    }
                }, status=400)

            # Suppression des détails sélectionnés
            delete_ids = request.POST.getlist('delete_detaille_ids')
            if delete_ids:
                for id_ in delete_ids:
                    try:
                        detaille_obj = produit.detailleproduit.get(id=id_)
                        # Supprimer le fichier du stockage si nécessaire
                        if detaille_obj.detaille_image:
                            detaille_obj.detaille_image.delete(save=False)
                        if detaille_obj.detaille_file:
                            detaille_obj.detaille_file.delete(save=False)
                        detaille_obj.delete()
                    except:
                        pass  # Optionnel : log l’erreur
            
            nb_existantes = DetailleProduit.objects.filter(detaille_produit=produit).count()
            nb_nouvelles = len(detaille_images)

            if nb_existantes + nb_nouvelles > 11:
                return JsonResponse({
                    'errors': {'form_errors': {'detaille_image': "Maximum 10 images autorisées."}}
                }, status=400)
        

            for image in detaille_images:
                image_compressée = compress_image(image)
                DetailleProduit.objects.create(
                    detaille_produit=produit,
                    detaille_image=image_compressée
                )

            if detaille_file and detaille_file.content_type.startswith('video'):
                video_compressée = compresser_video(detaille_file)
                DetailleProduit.objects.create(
                    detaille_produit=produit,
                    detaille_file=video_compressée
                )

            produit = produit_form.save()   # Sauvegarde du produit principal
            variation_formset.save()  # Sauvegarde des variations

            return JsonResponse({'message': 'Produit modifié avec succès !'}, status=200)

        # Préparation des erreurs pour la réponse
        errors = {
            'form_errors': produit_form.errors,
            'variation_formset_errors': variation_formset.errors,
        }
        
        return JsonResponse({'errors': errors}, status=400)




class VendeurDashboardView(LoginRequiredMixin, TemplateView):

    login_url = '/users/vendeur/login/'
    template_name = 'vendeur/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        try:
            _ = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')

        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        magasin = self.request.user.magasin
        produits = magasin.produits.all()
        context['produits'] = produits
        context['show_overlay'] = not self.request.user.is_active 
        return context

from django.db.models import Min, Sum

class VendeurProduitView(LoginRequiredMixin, TemplateView):
    login_url = '/users/vendeur/login/'
    template_name = 'vendeur/produits.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        try:
            _ = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        magasin = self.request.user.magasin
        produits = magasin.produits.annotate(
                    prix_minimum=Min('variations__prix'),
                    stock_total=Sum('variations__stock')
                )
        context['produits'] = produits
        return context

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class VendeurProfilView(LoginRequiredMixin, TemplateView):
    login_url = '/users/vendeur/login/'
    template_name = 'vendeur/profil.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        try:
            _ = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Tu peux ajouter des infos utilisateur/magasin ici si besoin
        context['magasin'] = self.request.user.magasin  # si tu veux afficher le magasin dans le profil
        return context

from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from vendeur.models import Produits

class ProduitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Produits
    template_name = 'vendeur/produit_confirm_delete.html'  # On peut garder un fallback (non utilisé ici)
    success_url = reverse_lazy('produit_vendeur')

    def test_func(self):
        produit = self.get_object()
        # Assure que le vendeur connecté est propriétaire du produit
        return self.request.user == produit.magasin.vendeur
    

    # views.py
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Magasin
from .forms import MagasinForm
from django.core.exceptions import ObjectDoesNotExist

class MagasinUpdateView(LoginRequiredMixin, View):
    login_url = '/users/vendeur/login/'

    def get(self, request):
        try:
            magasin = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')

        form = MagasinForm(instance=magasin)
        return render(request, 'vendeur/magasin_update_form.html', {'form': form})

    def post(self, request):
        try:
            magasin = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')

        form = MagasinForm(request.POST, request.FILES, instance=magasin)
        if form.is_valid():
            region = request.POST.get("region")
            district = request.POST.get("district")
            commune = request.POST.get("commune")
            fokontany = request.POST.get("fokontany")
            try:
                adresse = Adresse.objects.get(region=region, district=district, commune=commune, fokontany=fokontany)
                magasin.adresse_magasin = adresse
                magasin = form.save()  # Enregistre les autres champs
                magasin.save()        # Puis enregistre l’adresse mise à jour
                return redirect('vendeur_profil')
            except Adresse.DoesNotExist:
                form.add_error(None, "Adresse invalide.")
        
        # Si le form n’est pas valide ou adresse non trouvée
        return render(request, 'vendeur/magasin_update_form.html', {'form': form})


