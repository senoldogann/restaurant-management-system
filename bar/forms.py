from django import forms
from .models import Reservation, Drink
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'phone', 'date', 'time', 'guests', 'event', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6'),
                Column('guests', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('date', css_class='form-group col-md-6'),
                Column('time', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'event',
            'notes',
            Submit('submit', 'Rezervasyon Yap', css_class='btn btn-primary btn-lg mt-4')
        )
        
        # Sadece aktif etkinlikleri göster
        self.fields['event'].queryset = self.fields['event'].queryset.filter(is_active=True)

class ReviewForm(forms.Form):
    drink = forms.ModelChoiceField(
        queryset=None,
        empty_label="İçecek seçin...",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        }),
        label='İçecek'
    )
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': True,
            'placeholder': '1-5 arası bir puan verin'
        }),
        label='Puan'
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'required': True,
            'placeholder': 'Deneyiminizi paylaşın...'
        }),
        label='Yorum'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['drink'].queryset = Drink.objects.filter(is_available=True).order_by('name')
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'drink',
            'rating',
            'comment',
            Submit('submit', 'Değerlendirmeyi Gönder', css_class='btn btn-primary')
        ) 