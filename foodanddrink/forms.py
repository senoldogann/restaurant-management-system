from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from restaurant.models import MenuItem
from bar.models import Drink
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'phone_number']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Kullanıcı adınızı girin'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Şifrenizi girin'
        })
        self.fields['remember_me'].widget.attrs.update({
            'class': 'form-check-input'
        })

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea) 