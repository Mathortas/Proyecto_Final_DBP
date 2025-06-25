from django import forms
from .models import Tarea

class TareaForm(forms.ModelForm):
    CATEGORIAS = [
        ('P1', 'Permanente 1'),
        ('P2', 'Permanente 2'),
        ('EP', 'Examen Parcial'),
        ('EF', 'Examen Final'),
    ]

    categoria = forms.ChoiceField(choices=CATEGORIAS, label='Nota Principal')
    peso_porcentaje = forms.DecimalField(label='Peso (%)', max_digits=5, decimal_places=2, min_value=0, max_value=100)

    class Meta:
        model = Tarea
        fields = ['nombre_tarea', 'fecha_entrega', 'estado', 'descripcion', 'peso_porcentaje', 'categoria']
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
