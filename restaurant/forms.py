from django import forms
from .models import Reservation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'phone', 'date', 'time', 'guests', 'notes']
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
            'notes',
            Submit('submit', 'Rezervasyon Yap', css_class='btn btn-primary btn-lg mt-4')
        ) 