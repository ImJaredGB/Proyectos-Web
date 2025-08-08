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
    path('api/habitaciones/<str:zona>/', obtener_habitaciones_por_zona, name='habitaciones_por_zona'),
    path('api/habitaciones/editar/<str:nomenclatura>/', editar_habitacion, name='editar_habitacion'),
    path('api/literas/listar/', listar_literas, name='listar_literas'),
    path('api/usuarios/listar/', listar_usuarios, name='listar_usuarios'),
]