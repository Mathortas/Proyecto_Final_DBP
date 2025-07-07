# my_ucsp/api_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Curso, Horario, Matricula, Tarea, Nota, CategoriaPrincipal
from .serializers import (
    CursoSerializer, HorarioSerializer, MatriculaSerializer,
    TareaSerializer, NotaSerializer, CategoriaPrincipalSerializer, 
    UserSerializer
    
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
    serializer_class = MatriculaSerializer
    permission_classes = [permissions.IsAuthenticated]

    
    def get_queryset(self):
        return Matricula.objects.filter(id_usuario=self.request.user)

class TareaViewSet(viewsets.ModelViewSet):
    serializer_class = TareaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Tarea.objects.filter(id_usuario=user)
        # Si la web necesita mostrar todas cuando no hay autenticación
        return Tarea.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            serializer.save(id_usuario=user)
        else:
            # Si quieres evitar que usuarios anónimos creen
            raise PermissionDenied("Debe autenticarse para crear tareas.")

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoriaPrincipalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoriaPrincipal.objects.all()
    serializer_class = CategoriaPrincipalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Devuelve los datos del usuario autenticado.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
