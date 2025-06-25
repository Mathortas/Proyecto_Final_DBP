from django.urls import path
from . import views  #Para vincular una función en "views.py" con su respectiva url
from . import rdf_views

urlpatterns = [
    path('accounts/login/', views.login_view, name='login'),
    
    path('', views.index, name='index'), 
    
    path('register/', views.register_view, name='register'),

    path('login/',    views.login_view,  name='login'),
    
    path('logout/',   views.logout_view, name='logout'),
    
    path('calendario/', views.calendario, name='calendario'),

    path('curso/<int:id_curso>/', views.curso_detalle, name='curso-detalle'),

    path('editar-perfil/', views.editar_perfil, name='editar-perfil'),
    
    path('perfil/', views.perfil, name='perfil'),

    path('matricular/', views.matricular_cursos, name='matricular'),

    path('curso/<int:id_curso>/add-tarea/', views.add_tarea, name='add-tarea'),
    
    path('tarea/<int:tarea_id>/update/', views.update_tarea, name='update-tarea'),

    path('tarea/<int:tarea_id>/add_nota/', views.add_nota, name='add-nota'),

    #path('rdf/', rdf_views.generar_rdf, name='generar_rdf'),

    path('perfil/rdf/', views.generar_rdf_usuario, name='generar_rdf_usuario'),
      
    path('tarea/<int:pk>/editar/', views.editar_tarea, name='editar_tarea'),

    path('curso/<int:id_curso>/notas/', views.notas_curso, name='notas_curso'),

]
