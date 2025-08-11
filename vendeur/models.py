from django.db import models
from django.conf import settings
from users.models import CustomUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

class Adresse(models.Model):
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    commune = models.CharField(max_length=100)
    fokontany = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Nettoyage et mise en forme
        self.region = self.region.strip().lower().title()
        self.district = self.district.strip().lower().title()
        self.commune = self.commune.strip().lower().title()
        self.fokontany = self.fokontany.strip().lower().title()
        super().save(*args, **kwargs)

    def __str__(self):
        parties = [self.fokontany, self.commune, self.district, self.region]
        return ", ".join([p for p in parties if p])
    
class Magasin(models.Model):
    vendeur = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='magasin')
    nom_magasin = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logo_magasin', blank=True, null=True)
    lien_page_facebook = models.CharField()
    adresse_magasin = models.ForeignKey(Adresse, on_delete=models.SET_NULL, null=True) 
    precision_adresse = models.CharField(max_length=150, blank=True, null=True)   
    date_inscription = models.DateField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.nom_magasin:
            self.nom_magasin = self.nom_magasin.title()
        if self.precision_adresse:
            self.precision_adresse = self.precision_adresse.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_magasin} - {self.vendeur.phone}"

class Produits(models.Model):
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE, related_name='produits')
    nom_produit = models.CharField(max_length=100)
    description = models.CharField(max_length=180)
    moq = models.IntegerField(default=1)
    image_profil_produit = models.ImageField(upload_to='image_profil_produit')
    mot_clet = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    modele_livraison = models.ForeignKey('ModeleLivraison', on_delete=models.SET_NULL, null=True, help_text="frais de livraison appliqué à ce produit")


    # Champs promo globale (pour tout le produit)
    promo_active = models.BooleanField(default=False)
    reduction_pourcentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Pourcentage de réduction (0-100)"
    )
    promo_debut = models.DateTimeField(null=True, blank=True)
    promo_fin = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.nom_produit:
            self.nom_produit = self.nom_produit.title()
        if self.mot_clet:
            self.mot_clet = self.mot_clet.lower()  # souvent les mots-clés sont en minuscule
        if self.description:
            self.description = self.description.capitalize()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_produit} de {self.magasin.nom_magasin}"
    
    def est_nouveau(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).days < 7
    
    
    def promo_est_active(self):
        """Vrai si la promo est active actuellement sur ce produit."""
        maintenant = timezone.now()
        return (
            self.promo_active
            and self.reduction_pourcentage is not None
            and self.promo_debut is not None
            and self.promo_fin is not None
            and self.promo_debut <= maintenant <= self.promo_fin
        )

    def clean(self):
        super().clean()
        if self.reduction_pourcentage is not None and self.reduction_pourcentage > 100:
            raise ValidationError("La réduction ne peut pas dépasser 100%.")
        if self.promo_debut and self.promo_fin and self.promo_fin < self.promo_debut:
            raise ValidationError("La date de fin doit être après la date de début.")
        
    def get_prix_minimum(self):
        variations = self.variations.all()
        if not variations.exists():
            return None  # Ou un prix par défaut
        prix_min = min(variation.prix for variation in variations)
        if self.promo_est_active():
            reduction = self.reduction_pourcentage or Decimal(0)
            prix_promo = prix_min * (1 - reduction / Decimal(100))
            return round(prix_promo, 2)
        return prix_min

    def get_stock_total(self):
        return sum(variation.stock for variation in self.variations.all())

class VariationProduit(models.Model):
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE, related_name='variations')
    nom_variation = models.CharField(max_length=100)
    image_variation = models.ImageField(upload_to='image_variation', blank=True, null=True)
    prix = models.IntegerField()
    stock = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.nom_variation:
            self.nom_variation = self.nom_variation.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_variation} ({self.produit.nom_produit})"

    def get_prix_actuel(self):
        """
        Retourne le prix après application de la promo produit s'il y en a une.
        """
        if self.produit.promo_est_active():
            reduction = self.produit.reduction_pourcentage or Decimal(0)
            prix_promo = self.prix * (1 - reduction / Decimal(100))
            return round(prix_promo, 2)
        return self.prix

class DetailleProduit(models.Model):
    detaille_produit = models.ForeignKey(Produits, on_delete=models.CASCADE, related_name='detailleproduit')
    detaille_image = models.ImageField(upload_to='detaille_produit')
    detaille_file = models.FileField(upload_to='detaille_video', blank=True, null=True)

    def __str__(self):
        return f"Détail de {self.detaille_produit.nom_produit}"


class ModeleLivraison(models.Model):
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    delai_livraison_generale = models.CharField(max_length=100)
    calcul_par = models.CharField(max_length=10, choices=[('lanja', 'lanja'), ('isa', 'isa')], default='isa')
    gratuit_a_partir_de_prix = models.IntegerField(null=True, blank=True, help_text="Montant minimum pour la livraison gratuite")

    class Meta:
        unique_together = ('magasin', 'nom')

    def save(self, *args, **kwargs):
        if self.nom:
            self.nom = self.nom.title()
        if self.delai_livraison_generale:
            self.delai_livraison_generale = self.delai_livraison_generale.capitalize()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.get_calcul_par_display()})"

class ZoneLivraison(models.Model):
    modele = models.ForeignKey(ModeleLivraison, on_delete=models.CASCADE, related_name="zones")
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE)
    frais_base = models.IntegerField()    
    frais_par_supplement = models.IntegerField(blank=True, null=True)
    delai_livraison_zone = models.CharField(max_length=100)
    unite_supplement = models.IntegerField()


    class Meta:
        unique_together = ('modele', 'adresse')

    def save(self, *args, **kwargs):
        if self.delai_livraison_zone:
            self.delai_livraison_zone = self.delai_livraison_zone.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.adresse} - Base: {self.frais_base} + Supplément: {self.frais_par_supplement}"

class HorsZoneLivraison(models.Model):
    modele = models.ForeignKey(ModeleLivraison, on_delete=models.CASCADE, related_name='horszones')
    frais_base = models.IntegerField() 
    unite_supplement = models.IntegerField()
    frais_par_supplement = models.IntegerField(blank=True, null=True)
    delai_livraison_horszone = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if self.delai_livraison_horszone:
            self.delai_livraison_horszone = self.delai_livraison_horszone.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Hors zone - Base: {self.frais_base} + Supplément: {self.frais_par_supplement}"

