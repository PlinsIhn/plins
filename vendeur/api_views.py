from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Adresse

class RegionList(APIView):
    def get(self, request):
        regions = Adresse.objects.values_list('region', flat=True).distinct()
        return Response(sorted(regions))

class DistrictList(APIView):
    def get(self, request):
        region = request.query_params.get('region')
        if not region:
            return Response([])
        districts = Adresse.objects.filter(region=region).values_list('district', flat=True).distinct()
        return Response(sorted(districts))

class CommuneList(APIView):
    def get(self, request):
        region = request.query_params.get('region')
        district = request.query_params.get('district')
        if not (region and district):
            return Response([])
        communes = Adresse.objects.filter(region=region, district=district).values_list('commune', flat=True).distinct()
        return Response(sorted(communes))

class FokontanyList(APIView):
    def get(self, request):
        region = request.query_params.get('region')
        district = request.query_params.get('district')
        commune = request.query_params.get('commune')
        if not (region and district and commune):
            return Response([])
        fokontanys = Adresse.objects.filter(
            region=region,
            district=district,
            commune=commune
        ).values_list('fokontany', flat=True).distinct()
        return Response(sorted(fokontanys))


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Adresse

class AdresseIdView(APIView):
    def get(self, request):
        region = request.query_params.get('region')
        district = request.query_params.get('district')
        commune = request.query_params.get('commune')
        fokontany = request.query_params.get('fokontany')

        try:
            adresse = Adresse.objects.get(
                region=region,
                district=district,
                commune=commune,
                fokontany=fokontany
            )
            return Response({'id': adresse.id})
        except Adresse.DoesNotExist:
            return Response({'error': 'Adresse introuvable'}, status=404)
