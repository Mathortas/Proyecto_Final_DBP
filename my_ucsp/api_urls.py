# my_ucsp/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .api_views import (
    CursoViewSet, HorarioViewSet, MatriculaViewSet,
    TareaViewSet, NotaViewSet, CategoriaPrincipalViewSet,
    current_user,            # ← importa tu nueva vista
)


router = DefaultRouter()
router.register(r'cursos', CursoViewSet)
router.register(r'horarios', HorarioViewSet)
router.register(r'matriculas', MatriculaViewSet, basename='matricula')
router.register(r'tareas', TareaViewSet)
router.register(r'notas', NotaViewSet)
router.register(r'categorias', CategoriaPrincipalViewSet)

urlpatterns = [
    # JWT
    path('token/',        TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/',TokenRefreshView.as_view(),     name='token_refresh'),
    # Perfil
    path('users/me/',     current_user,                   name='current-user'),
    # Resto del router
] + router.urls
