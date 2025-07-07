from rest_framework import serializers
from .models import (
    Curso, Horario, Matricula, Tarea, Nota, CategoriaPrincipal
)
from django.contrib.auth.models import User

class CategoriaPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPrincipal
        fields = ['id_categoria', 'nombre']

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['id_curso', 'nombre', 'ciclo', 'modalidad', 'descripcion', 'creditos']

class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = ['id_horario', 'id_curso', 'dia_semana', 'hora_inicio', 'hora_fin', 'aula']

class MatriculaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matricula
        fields = ['id_matricula', 'id_usuario', 'id_curso', 'ciclo', 'fecha_matricula']

class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = [
            'id_tarea', 'nombre_tarea', 'descripcion', 'fecha_entrega',
            'estado', 'id_usuario', 'id_curso',
            'id_categoria', 'peso_porcentaje'
        ]

class NotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nota
        fields = [
            'id_nota', 'id_categoria', 'id_tarea', 'id_matricula',
            'nombre_nota', 'nota_obtenida', 'peso_porcentaje'
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email']
