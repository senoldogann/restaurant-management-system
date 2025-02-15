from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Review
from restaurant.models import MenuItem
from bar.models import Drink
from django.contrib.auth.forms import AuthenticationForm

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'phone_number']

class ReviewForm(forms.Form):
    menu_item = forms.ModelChoiceField(
        queryset=MenuItem.objects.filter(is_available=True).order_by('name'),
        empty_label="Menü öğesi seçin...",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        })
    )
    
    drink = forms.ModelChoiceField(
        queryset=Drink.objects.filter(is_available=True).order_by('name'),
        empty_label="İçecek seçin...",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        })
    )
    
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True,
            'placeholder': '1-5 arası bir puan verin'
        })
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'required': True,
            'placeholder': 'Deneyiminizi paylaşın...'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        menu_item = cleaned_data.get('menu_item')
        drink = cleaned_data.get('drink')
        
        if not menu_item and not drink:
            raise forms.ValidationError('Lütfen bir menü öğesi veya içecek seçin.')
        
        if menu_item and drink:
            raise forms.ValidationError('Lütfen sadece bir menü öğesi veya içecek seçin.')
        
        return cleaned_data 

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