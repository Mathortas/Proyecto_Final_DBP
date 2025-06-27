from rest_framework import viewsets, permissions
from .models import Curso, Horario, Matricula, Tarea, Nota, CategoriaPrincipal
from .serializers import (
    CursoSerializer, HorarioSerializer, MatriculaSerializer,
    TareaSerializer, NotaSerializer, CategoriaPrincipalSerializer
)

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer
    permission_classes = [permissions.IsAuthenticated]

class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer
    permission_classes = [permissions.IsAuthenticated]

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoriaPrincipalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoriaPrincipal.objects.all()
    serializer_class = CategoriaPrincipalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
