# my_ucsp/api_urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .api_views import (
    CursoViewSet, HorarioViewSet, MatriculaViewSet,
    TareaViewSet, NotaViewSet, CategoriaPrincipalViewSet
)

router = DefaultRouter()
router.register(r'cursos', CursoViewSet)
router.register(r'horarios', HorarioViewSet)
router.register(r'matriculas', MatriculaViewSet)
router.register(r'tareas', TareaViewSet)
router.register(r'notas', NotaViewSet)
router.register(r'categorias', CategoriaPrincipalViewSet)

urlpatterns = [
    # 🚀 ENDPOINTS JWT que faltaban
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Suma los del router
urlpatterns += router.urls
