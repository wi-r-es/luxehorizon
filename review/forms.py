from django import forms

class ReviewForm(forms.Form):
    review = forms.CharField(widget=forms.Textarea, label='Review')
    rating = forms.ChoiceField(choices=[(str(i), f'{i} Estrelas') for i in range(1, 6)], label='Avaliação')
    id = forms.CharField(widget=forms.HiddenInput)