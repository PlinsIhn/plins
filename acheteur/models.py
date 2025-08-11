from django.db import models
from vendeur.models import Adresse
from django.conf import settings

class AdresseAcheteur(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="adresses")
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE )
    nom_adresse = models.CharField( max_length=100, blank=True, null=True)  # Exemple: "Maison", "Travail"
    precision_adresse = models.CharField(max_length=150, blank=True, null=True)   

    est_defaut = models.BooleanField(default=False)  # Pour marquer une adresse principale

    def __str__(self):
        return f"{self.nom_adresse or 'Adresse'} - {self.user}"
