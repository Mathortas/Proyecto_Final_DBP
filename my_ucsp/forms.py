from django import forms
from .models import Tarea, CategoriaPrincipal, CursoCategoria

class TareaForm(forms.ModelForm):
    id_categoria = forms.ModelChoiceField(
        queryset=CategoriaPrincipal.objects.filter(nombre__in=[
            'Nota Permanente', 'Examen Parcial', 'Examen Final'
        ]),
        label='Nota Principal',
        empty_label="(Selecciona categoría)",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    subcategoria = forms.ModelChoiceField(
        queryset=CategoriaPrincipal.objects.filter(nombre__in=['Permanente 1', 'Permanente 2']),
        label='Subcategoría Permanente',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    tipo = forms.ChoiceField(
        choices=[],  # Se llenará dinámicamente
        label='Tipo',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = Tarea
        fields = ['nombre_tarea', 'fecha_entrega', 'descripcion', 'id_categoria', 'subcategoria', 'tipo']
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.curso = kwargs.pop('curso', None)
        super().__init__(*args, **kwargs)

        # Generar choices de tipo con pesos del curso
        tipo_a_nombre = {
            'TAREA': 'Tarea',
            'PRACTICA_GRUPAL': 'Práctica Grupal',
            'PRACTICA_INDIVIDUAL': 'Práctica Individual',
            'CONTROL': 'Control',
        }
        tipo_choices = []
        if self.curso:
            for clave, nombre in tipo_a_nombre.items():
                cat = CategoriaPrincipal.objects.filter(nombre=nombre).first()
                peso = 0
                if cat:
                    rel = CursoCategoria.objects.filter(id_curso=self.curso, id_categoria=cat).first()
                    if rel:
                        peso = float(rel.peso)
                tipo_choices.append((clave, f"{nombre} ({peso}%)"))
        else:
            tipo_choices = [(clave, nombre) for clave, nombre in tipo_a_nombre.items()]
        self.fields['tipo'].choices = tipo_choices

        # Determinar visibilidad de subcategoria y tipo
        cat_id = None
        if 'id_categoria' in self.data:
            try:
                cat_id = int(self.data.get('id_categoria'))
            except (ValueError, TypeError):
                cat_id = None
        elif self.instance and getattr(self.instance, 'id_categoria_id', None):
            cat_id = self.instance.id_categoria_id

        if cat_id:
            categoria = CategoriaPrincipal.objects.filter(pk=cat_id).first()
            if categoria and categoria.nombre == 'Nota Permanente':
                self.fields['subcategoria'].widget = forms.Select(attrs={'class': 'form-select'})
                self.fields['subcategoria'].required = True
                self.fields['tipo'].widget = forms.RadioSelect(attrs={'class': 'form-check-input'})
                self.fields['tipo'].required = True
            else:
                self.fields['subcategoria'].widget = forms.HiddenInput()
                self.fields['subcategoria'].required = False
                self.fields['tipo'].widget = forms.HiddenInput()
                self.fields['tipo'].required = False

        # Inicializar valores al editar
        if self.instance and getattr(self.instance, 'id_categoria_id', None):
            if self.instance.id_categoria.nombre in ['Permanente 1', 'Permanente 2']:
                self.initial['id_categoria'] = CategoriaPrincipal.objects.get(nombre='Nota Permanente')
                self.initial['subcategoria'] = self.instance.id_categoria

    def save(self, commit=True):
        instancia = super().save(commit=False)

        # Si hay subcategoria (tarea/práctica/control) y tipo
        sub = self.cleaned_data.get('subcategoria')
        tipo = self.cleaned_data.get('tipo')
        if sub and tipo:
            instancia.id_categoria = sub
            tipo_pesos = {
                'TAREA': 10.00,
                'PRACTICA_GRUPAL': 15.00,
                'PRACTICA_INDIVIDUAL': 20.00,
                'CONTROL': 25.00,
            }
            instancia.peso_porcentaje = tipo_pesos.get(tipo, 0)
        else:
            # Exámenes: peso desde CursoCategoria
            if self.curso and instancia.id_categoria:
                rel = CursoCategoria.objects.filter(id_curso=self.curso, id_categoria=instancia.id_categoria).first()
                instancia.peso_porcentaje = rel.peso if rel else 0
            else:
                instancia.peso_porcentaje = 0

        if commit:
            instancia.save()
        return instancia

