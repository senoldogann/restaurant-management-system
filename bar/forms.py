from django import forms
from .models import Event, Reservation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'phone', 'date', 'time', 'guests', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
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
            'notes',
            Submit('submit', 'Rezervasyon Yap', css_class='btn btn-primary btn-lg mt-4')
        )

class EventReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'phone', 'event', 'guests', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'event': forms.Select(attrs={'class': 'form-control'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece aktif etkinlikleri göster
        self.fields['event'].queryset = Event.objects.filter(is_active=True) 