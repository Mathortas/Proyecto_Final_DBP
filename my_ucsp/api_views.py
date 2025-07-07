from django.core.exceptions import PermissionDenied
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


# ✅ Cursos: visibles para todos (o solo autenticados si quieres)
class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ✅ Horarios: visibles para todos (o solo autenticados si quieres)
class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ✅ Matrículas: SOLO las del usuario autenticado
class MatriculaViewSet(viewsets.ModelViewSet):
    serializer_class = MatriculaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Matricula.objects.filter(id_usuario=self.request.user)


# ✅ Tareas: SOLO las creadas por el usuario autenticado
class TareaViewSet(viewsets.ModelViewSet):
    serializer_class = TareaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        print(">>> get_queryset() request.user =", user, "| is_authenticated =", user.is_authenticated)
        if user.is_authenticated:
            return Tarea.objects.filter(id_usuario=user)
        return Tarea.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        print(">>> perform_create() request.user =", user, "| is_authenticated =", user.is_authenticated)
        if user.is_authenticated:
            serializer.save(id_usuario=user)
        else:
            raise PermissionDenied("Debe autenticarse para crear tareas.")

class NotaViewSet(viewsets.ModelViewSet):
    serializer_class = NotaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Nota.objects.filter(id_matricula__id_usuario=user)
        return Nota.objects.all()


# ✅ Categorías: visibles para todos (o solo autenticados)
class CategoriaPrincipalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoriaPrincipal.objects.all()
    serializer_class = CategoriaPrincipalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ✅ Endpoint que devuelve datos del usuario autenticado
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
