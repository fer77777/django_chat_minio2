from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'codigo',
            'nombre',
            'categoria',
            'precio',
            'cantidad_existente',
            'estado',
            'fecha_ingreso',
            'porcentaje_cacao',
            'origen_cacao',
            'descripcion',
            'imagen',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-amber-900/30 bg-amber-50/50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-700',
                'placeholder': 'Ej. CHOC-001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-amber-900/30 bg-amber-50/50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-700',
                'placeholder': 'Ej. Barra Cacao Salvaje 85%'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-amber-900/30 bg-amber-50/50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-700'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-amber-900/30 bg-amber-50/50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-700',
                'placeholder': '0.00',
                'step': '0.50'
            }),
            'cantidad_existente': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-amber-900/30 bg-amber-50/50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-700',
                'placeholder': '0'
            }),
            'estado': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-amber-800 bg-amber-50 border-amber-900/30 rounded focus:ring-amber-700 focus:ring-2'
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-amber-900/30 bg-amber-50/50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-700'
            }),
            'porcentaje_cacao': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-amber-900/30 bg-amber-50/50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-700',
                'placeholder': 'Ej. 70',
                'min': '0',
                'max': '100'
            }),
            'origen_cacao': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-amber-900/30 bg-amber-50/50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-700',
                'placeholder': 'Ej. Alto Beni, La Paz'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-amber-900/30 bg-amber-50/50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-amber-700',
                'rows': 3,
                'placeholder': 'Notas aromáticas, ingredientes, maridaje...'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'w-full text-sm text-amber-900 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-amber-800 file:text-amber-50 hover:file:bg-amber-900 cursor-pointer'
            }),
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_cantidad_existente(self):
        cantidad = self.cleaned_data.get('cantidad_existente')
        if cantidad is not None and cantidad < 0:
            raise forms.ValidationError("La cantidad no puede ser negativa.")
        return cantidad
