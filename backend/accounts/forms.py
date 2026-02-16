from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import ContractorProfile, MusicianProfile, Profile, Role


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    display_name = forms.CharField(max_length=150, required=False)
    city = forms.CharField(max_length=80, required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))
    is_public = forms.BooleanField(required=False, initial=True)
    musician = forms.BooleanField(required=False, initial=True, label="Musico")
    contractor = forms.BooleanField(required=False, label="Contratante")
    phone = forms.CharField(max_length=20, required=False)
    state = forms.CharField(max_length=2, required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "state",
            "password1",
            "password2",
        )

    def selected_role_keys(self):
        role_keys = []
        if self.cleaned_data.get("musician"):
            role_keys.append(Role.Key.MUSICIAN)
        if self.cleaned_data.get("contractor"):
            role_keys.append(Role.Key.CONTRACTOR)
        return role_keys


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["display_name", "city", "bio", "is_public"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 5}),
        }


class RolesForm(forms.Form):
    musician = forms.BooleanField(required=False, label="Musico")
    contractor = forms.BooleanField(required=False, label="Contratante")

    def selected_role_keys(self):
        role_keys = []
        if self.cleaned_data.get("musician"):
            role_keys.append(Role.Key.MUSICIAN)
        if self.cleaned_data.get("contractor"):
            role_keys.append(Role.Key.CONTRACTOR)
        return role_keys


class MusicianProfileForm(forms.ModelForm):
    class Meta:
        model = MusicianProfile
        fields = [
            "instruments",
            "genres",
            "available_for_gigs",
            "spotify_url",
            "youtube_url",
            "instagram_url",
        ]
        widgets = {
            "instruments": forms.Textarea(attrs={"rows": 3}),
            "genres": forms.Textarea(attrs={"rows": 3}),
        }


class ContractorProfileForm(forms.ModelForm):
    class Meta:
        model = ContractorProfile
        fields = ["company_name", "company_website"]
