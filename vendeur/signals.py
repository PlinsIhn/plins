from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Produits, VariationProduit, DetailleProduit

# ============================================================
# 🗑 SUPPRESSION DES FICHIERS CLOUDINARY LORSQUE L'OBJET EST SUPPRIMÉ
# ============================================================

@receiver(post_delete, sender=Produits)
def delete_produit_files(sender, instance, **kwargs):
    """Supprimer l'image de profil du produit après suppression."""
    if instance.image_profil_produit:
        instance.image_profil_produit.delete(save=False)

@receiver(post_delete, sender=VariationProduit)
def delete_variation_files(sender, instance, **kwargs):
    """Supprimer l'image de variation après suppression."""
    if instance.image_variation:
        instance.image_variation.delete(save=False)

@receiver(post_delete, sender=DetailleProduit)
def delete_detaille_files(sender, instance, **kwargs):
    """Supprimer les images et vidéos de détail après suppression."""
    if instance.detaille_image:
        instance.detaille_image.delete(save=False)
    if instance.detaille_file:
        instance.detaille_file.delete(save=False)


