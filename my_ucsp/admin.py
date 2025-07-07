from django.contrib import admin
from .models import CursoCategoria

@admin.register(CursoCategoria)
class CursoCategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_curso', 'id_categoria', 'peso')
    list_filter = ('id_curso', 'id_categoria')
    search_fields = ('id_curso__nombre', 'id_categoria__nombre')
