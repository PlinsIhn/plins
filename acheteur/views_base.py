# acheteur/views_base.py
from django.views.generic import ListView
from django.db.models import Min
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage

class BaseInfiniteScrollView(ListView):
    """
    Vue de base réutilisable pour les listes de produits :
    - pagination dynamique via ?page_size=...
    - support AJAX (scroll infini)
    - annotation prix_min
    - template flexible (utilise celui défini dans la sous-classe)
    """
    context_object_name = 'produits'
    paginate_by = 8  # valeur par défaut si page_size non fournie

    def get_queryset(self):
        """
        Par défaut, on annote le prix minimal et on trie par date.
        Les sous-classes peuvent redéfinir get_queryset().
        """
        return super().get_queryset().annotate(
            prix_min=Min('variations__prix')
        ).order_by('-id')

    def get_paginate_by(self, queryset):
        """
        Permet au front d’envoyer ?page_size=... pour adapter le nombre d’items.
        """
        page_size = self.request.GET.get('page_size')
        if page_size and page_size.isdigit():
            return int(page_size)
        return self.paginate_by

    def get(self, request, *args, **kwargs):
        """
        Gère à la fois :
        - la requête normale (HTML complet)
        - la requête AJAX (scroll infini)
        """
        queryset = self.get_queryset()
        paginate_by = self.get_paginate_by(queryset)
        paginator = Paginator(queryset, paginate_by)
        page_number = request.GET.get('page', 1)

        try:
            page_obj = paginator.page(page_number)
        except (EmptyPage, ValueError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'produits_html': '', 'has_next': False})
            page_obj = paginator.page(paginator.num_pages)

        # Si AJAX → renvoyer juste le fragment HTML
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            produits_html = render_to_string(
                self.get_ajax_template_name(),
                {'produits': page_obj.object_list},
                request=request
            )
            return JsonResponse({
                'produits_html': produits_html,
                'has_next': page_obj.has_next()
            })

        # Sinon → rendu complet
        self.object_list = page_obj.object_list
        context = self.get_context_data(object_list=page_obj)
        return self.render_to_response(context)

    def get_ajax_template_name(self):
        """
        Permet de définir un template spécifique pour le fragment AJAX
        (par défaut : 'acheteur/includes/produits_list.html')
        """
        return getattr(self, 'ajax_template_name', 'acheteur/includes/produits_list.html')
