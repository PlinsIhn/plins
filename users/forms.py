from django import forms
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    phone = forms.CharField(label="Numéro de téléphone", max_length=20)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        password = cleaned_data.get("password")

        user = authenticate(phone=phone, password=password)

        if not user:
            raise forms.ValidationError("Numéro ou mot de passe incorrect.")

        cleaned_data["user"] = user
        return cleaned_data
