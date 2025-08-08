from django.urls import path
from .views import *

urlpatterns = [
    # URL para las vistas
    path('', login_view, name='login'),
    path('register/', registro_residente_view, name='registro'),
    path('home/', home_view, name='home'),
    path('usuarios/', usuarios_view, name='calendario'),
    path('habitaciones/', habitaciones_view, name='habitaciones'),

    #URL para las APIs
    path('api/habitaciones/crear/', crear_habitacion, name='crear_habitacion'),
    path('api/habitaciones/listar/', listar_habitaciones, name='listar_habitaciones'),
    path('api/habitaciones/<str:zona>/', obtener_habitaciones_por_zona, name='habitaciones_por_zona'),
    path('api/habitaciones/editar/<str:nomenclatura>/', editar_habitacion, name='editar_habitacion'),
    path('api/literas/listar/<str:habitacion>/', listar_literas, name='listar_literas'),
    path('api/usuarios/listar/', listar_usuarios, name='listar_usuarios'),
    path('api/usuarios/editar/<int:usuario_id>/', editar_usuario, name='editar_usuario'),
    path('api/zonas/listar/', listar_zonas, name='listar_zonas'),
]