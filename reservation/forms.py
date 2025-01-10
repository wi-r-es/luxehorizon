from django import forms
from .models import Season

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['descriptive', 'begin_month', 'begin_day', 'end_month', 'end_day', 'rate']
        widgets = {
            'descriptive': forms.Select(attrs={'class': 'form-control'}),
            'begin_month': forms.NumberInput(attrs={'min': 1, 'max': 12, 'class': 'form-control'}),
            'begin_day': forms.NumberInput(attrs={'min': 1, 'max': 31, 'class': 'form-control'}),
            'end_month': forms.NumberInput(attrs={'min': 1, 'max': 12, 'class': 'form-control'}),
            'end_day': forms.NumberInput(attrs={'min': 1, 'max': 31, 'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'step': 0.01, 'class': 'form-control'}),
        }

