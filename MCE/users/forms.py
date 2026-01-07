from django import forms
from .models import UserProfile,UploadImage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# class SignupForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']

from django.contrib.auth.forms import AuthenticationForm
class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadImage
        fields = ['image', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }