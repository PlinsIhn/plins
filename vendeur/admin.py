from django.contrib import admin
from .models import Magasin, Produits

class MagasinAdmin(admin.ModelAdmin):
    list_display = ('nom_magasin', 'vendeur')
    search_fields = ('nom_magasin', 'vendeur__phone')
    list_filter = ('vendeur__is_active',)

admin.site.register(Magasin, MagasinAdmin)
admin.site.register(Produits)
