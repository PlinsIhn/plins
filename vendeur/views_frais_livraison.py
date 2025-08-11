from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from .models import ModeleLivraison
from .forms import ModeleLivraisonForm  
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.template.loader import render_to_string

class ModeleLivraisonCreateView(LoginRequiredMixin, CreateView):
    login_url = '/users/vendeur/login/'
    model = ModeleLivraison
    form_class = ModeleLivraisonForm
    success_url = reverse_lazy('liste_modele_livraison')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        try:
            _ = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['magasin'] = self.request.user.magasin
        return kwargs
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = self.get_form()
            html = render_to_string('vendeur/frais_livraison/partials/ajout_modele_livraison.html', {'form': form}, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


    def form_valid(self, form):
        form.instance.magasin = self.request.user.magasin
        form.save()
        messages.success(self.request, "Le modèle de livraison a été ajouté avec succès.")

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # ✅ On ne retourne plus le HTML du nouvel élément
            return JsonResponse({'success': True})

        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(
                'vendeur/frais_livraison/partials/ajout_modele_livraison.html',
                {'form': form},
                request=self.request
            )
            return JsonResponse({'success': False, 'html': html})

        return super().form_invalid(form)



class ModeleLivraisonListView(LoginRequiredMixin, ListView):
    login_url = '/users/vendeur/login/'
    model = ModeleLivraison
    template_name = 'vendeur/frais_livraison/liste_modele_livraison.html'
    context_object_name = 'modeles'

    def get_queryset(self):
        return ModeleLivraison.objects.filter(
            magasin=self.request.user.magasin
        ).prefetch_related('zones__adresse')


from django.views.generic.edit import UpdateView

from django.http import JsonResponse
from django.template.loader import render_to_string

class ModeleLivraisonUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/users/vendeur/login/'
    model = ModeleLivraison
    form_class = ModeleLivraisonForm
    template_name = 'vendeur/frais_livraison/edit_modele_livraison.html'
    success_url = reverse_lazy('liste_modele_livraison')

    def get_queryset(self):
        # Sécurité : le vendeur ne peut modifier que ses propres modèles
        return ModeleLivraison.objects.filter(magasin=self.request.user.magasin)
    
    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            messages.success(self.request, "Modifié avec succès")
            return JsonResponse({'success': True})
        else:
            messages.success(self.request, "avereno azafady")
            return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, {'form': form}, request=self.request)
            return JsonResponse({'success': False, 'html': html})
        else:
            return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Renvoyer uniquement le formulaire pour chargement modal via AJAX
            html = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modele'] = self.object
        return context

from django.http import JsonResponse
from django.views.generic import DeleteView

class ModeleLivraisonDeleteView(DeleteView):
    model = ModeleLivraison
    success_url = reverse_lazy('liste_modele_livraison')

    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False}, status=400)


from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist

from .models import ZoneLivraison, ModeleLivraison, Adresse
from .forms import ZoneLivraisonForm  # à créer si pas encore

from django.http import JsonResponse

class ZoneLivraisonCreateView(LoginRequiredMixin, CreateView):
    login_url = '/users/vendeur/login/'
    model = ZoneLivraison
    form_class = ZoneLivraisonForm
    template_name = 'vendeur/frais_livraison/ajout_zone_livraison.html'
    success_url = reverse_lazy('liste_modele_livraison')

    def dispatch(self, request, *args, **kwargs):
        try:
            self.magasin = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')

        self.modele = get_object_or_404(ModeleLivraison, pk=self.kwargs['modele_id'], magasin=self.magasin)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.modele = self.modele

        adresse_id = self.request.POST.get('adresse')
        if not adresse_id:
            form.add_error(None, "Mampidira adiresy complet")
            return self.form_invalid(form)

        try:
            adresse = Adresse.objects.get(pk=adresse_id)
            form.instance.adresse = adresse
        except Adresse.DoesNotExist:
            form.add_error(None, "Adresse invalide.")
            return self.form_invalid(form)

        if ZoneLivraison.objects.filter(modele=self.modele, adresse=adresse).exists():
            form.add_error(None, "Cette adresse est déjà ajoutée pour ce modèle de livraison.")
            return self.form_invalid(form)

        form.save()
        messages.success(self.request, "Zone de livraison ajoutée avec succès.")

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'success': True})

        return super().form_valid(form)


    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(self.request, 'vendeur/frais_livraison/ajout_zone_livraison.html', context)
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.object = None
        context = self.get_context_data()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'vendeur/frais_livraison/ajout_zone_livraison.html', context)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modele'] = self.modele
        return context


from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import ZoneLivraison, Adresse  # Bien importer Adresse
from .forms import ZoneLivraisonForm

from django.http import JsonResponse
from django.template.loader import render_to_string

class ZoneLivraisonUpdateView(LoginRequiredMixin, UpdateView):
    model = ZoneLivraison
    form_class = ZoneLivraisonForm
    template_name = 'vendeur/frais_livraison/edit_zone_livraison.html'

    def get_queryset(self):
        return ZoneLivraison.objects.filter(modele__magasin=self.request.user.magasin)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["zone"] = self.object
        return context

    def form_valid(self, form):
        adresse_id = self.request.POST.get('adresse')
        if adresse_id:
            try:
                adresse = Adresse.objects.get(id=adresse_id)
                form.instance.adresse = adresse
            except Adresse.DoesNotExist:
                form.add_error(None, "Adresse invalide sélectionnée.")
                return self.form_invalid(form)

        self.object = form.save()

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            messages.success(self.request, "Modifié avec succès")
            return JsonResponse({'success': True})
        else:
            return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Retourner juste le HTML du formulaire (pas JSON)
            return render(self.request, self.template_name, {'form': form, 'zone': self.object})
        return super().form_invalid(form)



from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView
from .models import ZoneLivraison

class ZoneLivraisonDeleteView(LoginRequiredMixin, DeleteView):
    model = ZoneLivraison
    success_url = reverse_lazy('liste_modele_livraison')

    def get_queryset(self):
        return ZoneLivraison.objects.filter(modele__magasin=self.request.user.magasin)

    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({'success': True})
        return super().post(request, *args, **kwargs)


from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from .models import HorsZoneLivraison, ModeleLivraison
from .forms import HorsZoneLivraisonForm

class HorsZoneLivraisonCreateView(LoginRequiredMixin, CreateView):
    login_url = '/users/vendeur/login/'  # URL de connexion si non connecté
    model = HorsZoneLivraison
    form_class = HorsZoneLivraisonForm
    template_name = 'vendeur/frais_livraison/ajout_horszone_livraison.html'
    success_url = reverse_lazy('liste_modele_livraison')

    def dispatch(self, request, *args, **kwargs):
        # Vérifie que l'utilisateur a un magasin associé
        try:
            self.magasin = request.user.magasin
        except ObjectDoesNotExist:
            return redirect('vendeur_magasin')

        # Vérifie que le modele appartient bien à ce magasin
        self.modele = get_object_or_404(ModeleLivraison, pk=self.kwargs['modele_id'], magasin=self.magasin)
        
        if HorsZoneLivraison.objects.filter(modele=self.modele).exists():
            messages.warning(request, "Efa misy hors zone io modèle io")
            return redirect('liste_modele_livraison')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.modele = self.modele
        self.object = form.save()
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            messages.success(self.request, "Hors zone ajouté avec succès")
            return JsonResponse({"success": True})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(self.template_name, self.get_context_data(form=form), request=self.request)
            return JsonResponse({"success": False, "html": html})
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        # Ajoute le modèle au contexte pour pouvoir afficher son nom dans le template
        context = super().get_context_data(**kwargs)
        context['modele'] = self.modele
        return context

from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import HorsZoneLivraison
from .forms import HorsZoneLivraisonForm

from django.http import JsonResponse
from django.template.loader import render_to_string

class HorsZoneLivraisonUpdateView(UpdateView):
    model = HorsZoneLivraison
    form_class = HorsZoneLivraisonForm
    template_name = 'vendeur/frais_livraison/edit_horszone_livraison.html'
    context_object_name = 'horszone'

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            messages.success(self.request, "Modifié avec succès")
            return JsonResponse({"success": True})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(self.template_name, self.get_context_data(form=form), request=self.request)
            return JsonResponse({"success": False, "html": html})
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('liste_modele_livraison')
 # Ou une autre redirection

class HorsZoneLivraisonDeleteView(DeleteView):
    model = HorsZoneLivraison
    template_name = 'vendeur/frais_livraison/delete_horszone_livraison.html'

    def get_success_url(self):
        return reverse_lazy('liste_modele_livraison')
