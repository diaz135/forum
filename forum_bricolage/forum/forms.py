# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Publication, Profile

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['titre', 'contenu', 'image']

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    pass

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nom', 'bio']