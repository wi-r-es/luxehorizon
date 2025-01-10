from django import forms
from .models import Season

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['descriptive', 'begin_month', 'begin_day', 'end_month', 'end_day', 'rate']
        widgets = {
            'begin_month': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'begin_day': forms.NumberInput(attrs={'min': 1, 'max': 31}),
            'end_month': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'end_day': forms.NumberInput(attrs={'min': 1, 'max': 31}),
            'rate': forms.NumberInput(attrs={'step': 0.01}),
        }

