from django import forms
from users.models import CustomUser

class VendeurSignUpForm(forms.ModelForm):
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput,
        help_text="Au moins 8 caractères, contenant A-Z, a-z et chiffres"
    )
    password2 = forms.CharField(
        label="Confirmez le mot de passe",
        widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ['phone', 'password', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Numéro invalide. Entrez exactement 10 chiffres.")
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Ce numéro est déjà utilisé.")
        return phone

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if not any(c.islower() for c in password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre minuscule.")
        if not any(c.isupper() for c in password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            self.add_error('password2', "Les mots de passe ne correspondent pas.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'vendeur'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

from django import forms
from .models import Magasin

class MagasinForm(forms.ModelForm):
    class Meta:
        model = Magasin
        fields = ['nom_magasin', 'logo', 'precision_adresse', 'lien_page_facebook']  # Ne pas inclure adresse_magasin

    def clean_logo(self):
        image = self.cleaned_data.get('logo')
        if image:
            return compress_image(image)
        return image

# forms.py (dans ton app vendeur ou produits)
from django import forms
from .models import Produits
from .utils import compress_image

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produits
        fields = [
            'nom_produit', 'description', 'moq', 'mot_clet', 'modele_livraison', 'image_profil_produit',
            'promo_active', 'reduction_pourcentage', 'promo_debut', 'promo_fin'
        ]
        widgets = {
            'promo_debut': forms.DateInput(attrs={'type': 'date'}),
            'promo_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        vendeur = kwargs.pop('vendeur', None)  # récupère l'utilisateur vendeur depuis la vue
        super().__init__(*args, **kwargs)

        if vendeur:
            # Filtre les modèles pour ne garder que ceux du magasin du vendeur
            self.fields['modele_livraison'].queryset = ModeleLivraison.objects.filter(
                magasin=vendeur.magasin
            )
            
    def clean_image_profil_produit(self):
        image = self.cleaned_data.get('image_profil_produit')
        if image:
            return compress_image(image)
        return image


from django import forms
from .models import VariationProduit

class VariationProduitForm(forms.ModelForm):
    class Meta:
        model = VariationProduit
        fields = ['nom_variation', 'image_variation', 'prix', 'stock']

    def clean_image_variation(self):
        image = self.cleaned_data.get('image_variation')
        if image:
            return compress_image(image)
        return image

# forms.py

from django import forms
from .models import DetailleProduit
from .utils import compresser_video

class DetailleProduitForm(forms.ModelForm):
    class Meta:
        model = DetailleProduit
        fields = ['detaille_image', 'detaille_file']

    def clean_detaille_image(self):
        image = self.cleaned_data.get('detaille_image')
        if image:
            return compress_image(image)
        return image
        

    def clean_detaille_file(self):
        video = self.cleaned_data.get('detaille_file')
        if video and video.content_type.startswith('video'):
            return compresser_video(video)

        return video


from django import forms
from .models import ModeleLivraison

class ModeleLivraisonForm(forms.ModelForm):
    class Meta:
        model = ModeleLivraison
        fields = ['nom', 'calcul_par', 'delai_livraison_generale', 'gratuit_a_partir_de_prix']
    
    def __init__(self, *args, **kwargs):
        self.magasin = kwargs.pop('magasin', None)
        super().__init__(*args, **kwargs)

    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if ModeleLivraison.objects.filter(magasin=self.magasin, nom=nom).exists():
            raise forms.ValidationError("Ce nom est déjà utilisé pour ce magasin.")
        return nom
    
from django import forms
from .models import ZoneLivraison

class ZoneLivraisonForm(forms.ModelForm):
    class Meta:
        model = ZoneLivraison
        fields = ['frais_base', 'unite_supplement', 'frais_par_supplement','delai_livraison_zone']
        exclude = ['modele', 'adresse']  # adresse est injectée manuellement

    # Tu peux ajouter clean ici pour t'assurer que l'adresse est bien reçue

from django import forms
from .models import HorsZoneLivraison

class HorsZoneLivraisonForm(forms.ModelForm):
    class Meta:
        model = HorsZoneLivraison
        # Le champ 'modele' est généralement exclu car lié automatiquement au modèle courant
        fields = ['frais_base', 'unite_supplement','frais_par_supplement', 'delai_livraison_horszone']
