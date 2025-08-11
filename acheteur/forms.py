from django import forms
from users.models import CustomUser

class AcheteurSignUpForm(forms.ModelForm):
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
        phone = self.cleaned_data['phone']
        password = self.cleaned_data['password']
        user = CustomUser.objects.create_user(phone=phone, password=password, role='acheteur')
        if commit:
            user.save()
        return user


from django import forms
from .models import AdresseAcheteur

class AdresseAcheteurForm(forms.ModelForm):
    class Meta:
        model = AdresseAcheteur
        fields = ['nom_adresse', 'precision_adresse', 'est_defaut']


