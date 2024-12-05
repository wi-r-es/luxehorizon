from django import forms
from .models import Hotel, Room, RoomType

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['h_name', 'full_address', 'postal_code', 'city', 'email', 'telephone', 'details', 'stars']
        labels = {
            'h_name': 'Nome do Hotel',
            'full_address': 'Morada',
            'postal_code': 'Código Postal',
            'city': 'Cidade',
            'email': 'E-mail',
            'telephone': 'Telefone',
            'details': 'Detalhes Adicionais',
            'stars': 'Nº de Estrelas',
        }
        widgets = {
            'h_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Hotel'}),
            'full_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Morada'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalhes'}),
            'stars': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['type', 'room_number', 'base_price', 'condition', 'capacity']
        widgets = {
            'condition': forms.Select(choices=[
                (0, 'Disponível'),
                (1, 'Sujo'),
                (2, 'Em Manutenção'),
            ])
        }
        labels = {
            'type': 'Tipo',
            'room_number': 'Nº do Quarto',
            'base_price': 'Preço Base (€)',
            'Estado': 'Condition',
            'capacity': 'Capacidade',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].queryset = RoomType.objects.all()
