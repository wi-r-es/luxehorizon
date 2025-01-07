from django import forms
from .models import Season

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['descriptive', 'begin_date', 'end_date', 'rate']

        widgets = {
            'descriptive': forms.TextInput(attrs={'class': 'form-control'}),
            'begin_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'rate': forms.NumberInput(attrs={'min': 0, 'max': 10}),
        }
