from django import forms
from .models import Tarea, CategoriaPrincipal

class TareaForm(forms.ModelForm):
    id_categoria = forms.ModelChoiceField(
        queryset=CategoriaPrincipal.objects.all(),
        label='Nota Principal',
        empty_label="(Selecciona categoría)",
        widget=forms.Select()
    )
    peso_porcentaje = forms.DecimalField(
        label='Peso (%)',
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100
    )

    class Meta:
        model = Tarea
        fields = [
            'nombre_tarea',
            'fecha_entrega',
            'descripcion',
            'peso_porcentaje',
            'id_categoria',
        ]
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
