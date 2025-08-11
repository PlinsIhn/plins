# adresse_app/serializers.py
from rest_framework import serializers
from .models import Adresse

class AdresseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adresse
        fields = ['id', 'region', 'district', 'commune', 'fokontany']
