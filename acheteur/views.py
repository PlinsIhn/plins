
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


class ListeProduitsView(ListView):
    model = Produits
    template_name = 'acheteur/liste_produits.html'
    context_object_name = 'produits'

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            prix_min=Min('variations__prix')  # 'variations' est le related_name de VariationProduit
        )
        return queryset


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
