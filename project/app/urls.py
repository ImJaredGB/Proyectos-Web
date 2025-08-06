from django.urls import path
from .views import registro_residente_view, login_view

urlpatterns = [
    path('registro/', registro_residente_view, name='registro'),
    path('login/', login_view, name='login'),
]