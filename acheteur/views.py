
from django.views.generic import ListView
from vendeur.models import Produits 
from django.db.models import Min
from django.views import View
from django.shortcuts import render, redirect
from .forms import AcheteurSignUpForm
from django.contrib import messages

class SignupAcheteurView(View):
    def get(self, request):
        form = AcheteurSignUpForm()
        return render(request, 'acheteur/signup_acheteur.html', {'form': form})

    def post(self, request):
        form = AcheteurSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre compte acheteur a été créé avec succès. Vous pouvez maintenant vous connecter.")
            return redirect('login_acheteur')
        return render(request, 'acheteur/signup_acheteur.html', {'form': form})

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AcheteurSignUpForm
from users.forms import LoginForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

class ProfilAcheteurView(LoginRequiredMixin, TemplateView):
    login_url = '/users/acheteur/login/'  # URL de connexion acheteur
    template_name = 'acheteur/profil_acheteur.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        # Vérifier que l'utilisateur est bien un acheteur
        if request.user.role != 'acheteur':
            return redirect(self.login_url)  # ou une page d'erreur

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acheteur'] = self.request.user  # ou self.request.user.acheteurprofil
        return context



from vendeur.models import Produits
from .views_base import BaseInfiniteScrollView

class ListeProduitsView(BaseInfiniteScrollView):
    model = Produits
    template_name = 'acheteur/liste_produits.html'
    ajax_template_name = 'acheteur/includes/produits_list.html'  # 👈 cohérent avec la base
    context_object_name = 'produits'





from django.views import View
from django.shortcuts import render, get_object_or_404
from vendeur.models import Produits, Magasin  # Import depuis app vendeur
from django.db.models import Min, Max

from django.db.models import Min, Max, F, ExpressionWrapper, FloatField

from django.db.models import Min, Max, F, ExpressionWrapper, FloatField
from django.shortcuts import get_object_or_404, render
from django.views import View
from vendeur.models import Produits

class ProduitDetailPublicView(View):
    def get(self, request, produit_id):
        produit = get_object_or_404(Produits, id=produit_id)
        variations = produit.variations.all()
        details = produit.detailleproduit.all().order_by('-detaille_file')  # vidéo d’abord

        # Par défaut (pas de promo)
        prix_min = variations.aggregate(Min('prix'))['prix__min']
        prix_max = variations.aggregate(Max('prix'))['prix__max']

        ancien_prix_min = ancien_prix_max = None

        if produit.promo_est_active():
            # Utilise reduction_pourcentage au lieu de promo_active
            pourcent = produit.reduction_pourcentage or 0
            coefficient = (100 - float(pourcent)) / 100

            variations_remise = variations.annotate(
                prix_remise=ExpressionWrapper(
                    F('prix') * coefficient,
                    output_field=FloatField()
                )
            )

            prix_min = variations_remise.aggregate(Min('prix_remise'))['prix_remise__min']
            prix_max = variations_remise.aggregate(Max('prix_remise'))['prix_remise__max']

            # Prix barrés pour affichage
            ancien_prix_min = variations.aggregate(Min('prix'))['prix__min']
            ancien_prix_max = variations.aggregate(Max('prix'))['prix__max']

        return render(request, 'acheteur/detail_produit.html', {
            'produit': produit,
            'variations': variations,
            'details': details,
            'prix_min': prix_min,
            'prix_max': prix_max,
            'ancien_prix_min': ancien_prix_min,
            'ancien_prix_max': ancien_prix_max,
        })


from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import AdresseAcheteur
from .forms import AdresseAcheteurForm

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AdresseAcheteurForm
from .models import Adresse, AdresseAcheteur

class AjouterAdresseAcheteurView(LoginRequiredMixin, View):
    login_url = '/users/acheteur/login/'

    def get(self, request):
        form = AdresseAcheteurForm()
        adresses = Adresse.objects.all()  # filtrer si besoin
        return render(request, 'acheteur/ajouter_adresse.html', {
            'form': form,
            'adresses': adresses
        })

    def post(self, request):
        form = AdresseAcheteurForm(request.POST)
        adresse_id = request.POST.get("adresse")

        if form.is_valid() and adresse_id:
            adresse_selectionnee = Adresse.objects.filter(id=adresse_id).first()
            if not adresse_selectionnee:
                form.add_error(None, "Adresse non valide.")
                return render(request, 'acheteur/ajouter_adresse.html', {'form': form})

            adresse_acheteur = form.save(commit=False)
            adresse_acheteur.user = request.user
            adresse_acheteur.adresse = adresse_selectionnee

            # Gestion de l'adresse par défaut
            # 1) Si aucune adresse pour cet utilisateur, on met celle-ci par défaut
            if not AdresseAcheteur.objects.filter(user=request.user).exists():
                adresse_acheteur.est_defaut = True
            else:
                # 2) Sinon si formulaire a un champ est_defaut coché, on remet à jour
                if 'est_defaut' in request.POST and request.POST.get('est_defaut') == 'on':
                    # Désactive les autres adresses par défaut
                    AdresseAcheteur.objects.filter(user=request.user, est_defaut=True).update(est_defaut=False)
                    adresse_acheteur.est_defaut = True
                else:
                    # Si aucune adresse par défaut existe encore (cas rare), on la met par défaut
                    if not AdresseAcheteur.objects.filter(user=request.user, est_defaut=True).exists():
                        adresse_acheteur.est_defaut = True

            adresse_acheteur.save()
            return redirect('liste_adresses')

        adresses = Adresse.objects.all()
        return render(request, 'acheteur/ajouter_adresse.html', {
            'form': form,
            'adresses': adresses
        })


class ModifierAdresseAcheteurView(LoginRequiredMixin, View):
    login_url = '/users/acheteur/login/'

    def get(self, request, pk):
        try:
            # Vérifier que l'adresse appartient bien à l'utilisateur connecté
            adresse_acheteur = AdresseAcheteur.objects.get(id=pk, user=request.user)
            form = AdresseAcheteurForm(instance=adresse_acheteur)
            adresses = Adresse.objects.all()
            
            return render(request, 'acheteur/modifier_adresse.html', {
                'form': form,
                'adresses': adresses,
                'adresse_acheteur': adresse_acheteur,
                'adresse_selectionnee': adresse_acheteur.adresse,
                'region_actuelle': adresse_acheteur.adresse.region,
                'district_actuel': adresse_acheteur.adresse.district,
                'commune_actuelle': adresse_acheteur.adresse.commune,
                'fokontany_actuel': adresse_acheteur.adresse.fokontany,
            })

        except AdresseAcheteur.DoesNotExist:
            return redirect('liste_adresses')

    def post(self, request, pk):
        try:
            adresse_acheteur = AdresseAcheteur.objects.get(id=pk, user=request.user)
            form = AdresseAcheteurForm(request.POST, instance=adresse_acheteur)
            adresse_id = request.POST.get("adresse")

            # Vérification que l'ID est bien un nombre valide
            if adresse_id and adresse_id.isdigit():
                adresse_selectionnee = Adresse.objects.filter(id=int(adresse_id)).first()
            else:
                adresse_selectionnee = None

            if form.is_valid() and adresse_selectionnee:
                adresse_acheteur = form.save(commit=False)
                adresse_acheteur.adresse = adresse_selectionnee

                # Gestion adresse par défaut
                if request.POST.get('est_defaut') == 'on':
                    AdresseAcheteur.objects.filter(
                        user=request.user, est_defaut=True
                    ).exclude(id=pk).update(est_defaut=False)
                    adresse_acheteur.est_defaut = True

                adresse_acheteur.save()
                return redirect('liste_adresses')

            # ⚡ Toujours renvoyer les valeurs actuelles même en cas d'erreur
            adresses = Adresse.objects.all()
            context = {
                'form': form,
                'adresses': adresses,
                'adresse_acheteur': adresse_acheteur,
                'adresse_selectionnee': adresse_selectionnee,
                'region_actuelle': adresse_selectionnee.region if adresse_selectionnee else "",
                'district_actuel': adresse_selectionnee.district if adresse_selectionnee else "",
                'commune_actuelle': adresse_selectionnee.commune if adresse_selectionnee else "",
                'fokontany_actuel': adresse_selectionnee.fokontany if adresse_selectionnee else "",
            }
            return render(request, 'acheteur/modifier_adresse.html', context)

        except AdresseAcheteur.DoesNotExist:
            return redirect('liste_adresses')








from django.views.generic import ListView

class ListeAdressesAcheteurView(LoginRequiredMixin, ListView):
    model = AdresseAcheteur
    template_name = 'acheteur/liste_adresses.html'
    context_object_name = 'adresses'

    def get_queryset(self):
        return AdresseAcheteur.objects.filter(user=self.request.user)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import AdresseAcheteur

class SupprimerAdresseAcheteurView(LoginRequiredMixin, View):
    login_url = '/users/acheteur/login/'

    def post(self, request, pk):
        adresse = get_object_or_404(AdresseAcheteur, pk=pk, user=request.user)
        adresse.delete()
        return redirect('liste_adresses')



from django.views.generic import ListView
from vendeur.models import Produits
from django.db.models import Q
from rapidfuzz import fuzz

class RechercheProduitView(BaseInfiniteScrollView):
    model = Produits
    template_name = "acheteur/resultats_recherche.html"
    ajax_template_name = "acheteur/includes/produits_list.html"  # 👈 pour le rendu AJAX
    context_object_name = "produits"


    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        region = self.request.GET.get('region', '').strip()
        produits = Produits.objects.select_related('magasin', 'magasin__adresse_magasin').prefetch_related('variations').all()

        # --- Si aucun mot clé, on retourne tout ---
        if not query:
            if region:
                produits = produits.filter(magasin__adresse_magasin__region__iexact=region)
            return produits

        # --- Calcul du score de similarité pour chaque produit ---
        produits_scores = []
        for produit in produits:
            texte = f"{produit.nom_produit} {produit.description} {produit.mot_clet or ''} {produit.magasin.nom_magasin if produit.magasin else ''}".lower()

            # Score principal sur le texte du produit
            score = fuzz.partial_ratio(query.lower(), texte)

            # Score secondaire sur les variations
            for variation in produit.variations.all():
                score = max(score, fuzz.partial_ratio(query.lower(), variation.nom_variation.lower()))

            if score > 50:  # on garde seulement les résultats pertinents
                produits_scores.append((produit, score))

        # --- Tri des produits du plus proche au moins proche ---
        produits_scores.sort(key=lambda x: x[1], reverse=True)

        # --- Extraction des produits triés ---
        produits_tries = [p for p, s in produits_scores]

        # --- Filtrage par région si applicable ---
        if region:
            produits_tries = [
                p for p in produits_tries
                if p.magasin and p.magasin.adresse_magasin
                and p.magasin.adresse_magasin.region.lower() == region.lower()
            ]

        return produits_tries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        region = self.request.GET.get('region', '').strip()
        produits = self.get_queryset()

        # Extraire les régions disponibles parmi les produits trouvés
        regions_disponibles = sorted(
            set(
                p.magasin.adresse_magasin.region
                for p in produits
                if p.magasin and p.magasin.adresse_magasin and p.magasin.adresse_magasin.region
            )
        )

        context["query"] = query
        context["regions"] = regions_disponibles
        context["selected_region"] = region
        return context

from vendeur.models import Produits, Magasin
from .views_base import BaseInfiniteScrollView
from django.shortcuts import get_object_or_404

class ProduitsMagasinView(BaseInfiniteScrollView):
    model = Produits
    template_name = "acheteur/magasin_detail.html"
    fragment_template = "acheteur/includes/produits_list.html"
    context_object_name = "produits"
    paginate_by = 6

    def get_queryset(self):
        magasin_id = self.kwargs.get("magasin_id")
        magasin = get_object_or_404(Magasin, id=magasin_id)
        return Produits.objects.filter(magasin=magasin).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        magasin_id = self.kwargs.get("magasin_id")
        context["magasin"] = get_object_or_404(Magasin, id=magasin_id)
        
        # ✅ récupérer le paramètre ?from=...
        produit_id = self.request.GET.get("from")
        context["produit_retour_id"] = produit_id
        return context


from django.shortcuts import get_object_or_404
from vendeur.models import Produits, Magasin
from .views_base import BaseInfiniteScrollView

from django.shortcuts import get_object_or_404
from vendeur.models import Produits, Magasin
from .views_base import BaseInfiniteScrollView
from rapidfuzz import fuzz

class RechercheProduitsMagasinView(BaseInfiniteScrollView):
    template_name = "acheteur/recherche_produits_magasin.html"
    ajax_template_name = "acheteur/includes/produits_list.html"

    def get_queryset(self):
        magasin_id = self.kwargs.get("magasin_id")
        magasin = get_object_or_404(Magasin, id=magasin_id)
        query = self.request.GET.get("q", "").strip()

        # On ne prend que les produits de ce magasin
        produits = (
            Produits.objects
            .filter(magasin=magasin)
            .prefetch_related("variations")
            .all()
        )

        # Si aucun mot clé → on renvoie tout
        if not query:
            return produits.order_by("-id")

        # Calcul de similarité
        produits_scores = []
        for produit in produits:
            texte = f"{produit.nom_produit} {produit.description or ''} {produit.mot_clet or ''}".lower()
            score = fuzz.partial_ratio(query.lower(), texte)

            # Vérifie aussi les noms de variations
            for variation in produit.variations.all():
                score = max(score, fuzz.partial_ratio(query.lower(), variation.nom_variation.lower()))

            if score > 50:  # seuil de similarité
                produits_scores.append((produit, score))

        # Trie les produits du plus similaire au moins similaire
        produits_scores.sort(key=lambda x: x[1], reverse=True)

        # Récupère uniquement les objets Produits triés
        produits_tries = [p for p, s in produits_scores]

        return produits_tries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        magasin_id = self.kwargs.get("magasin_id")
        magasin = get_object_or_404(Magasin, id=magasin_id)
        context["magasin"] = magasin
        context["query"] = self.request.GET.get("q", "").strip()

        # ✅ récupère le produit d’origine (si transmis dans l’URL)
        produit_id = self.request.GET.get("from")
        context["produit_retour_id"] = produit_id
        return context

