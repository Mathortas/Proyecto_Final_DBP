
from rest_framework.routers import DefaultRouter
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

urlpatterns = router.urls
