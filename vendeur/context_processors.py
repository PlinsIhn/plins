from .models import Magasin

def magasin_context(request):
    if request.user.is_authenticated:
        try:
            return {'magasin': request.user.magasin}
        except Magasin.DoesNotExist:
            return {'magasin': None}
    return {'magasin': None}
