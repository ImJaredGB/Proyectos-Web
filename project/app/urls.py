from django.urls import path
from .views import registro_residente_view, login_view, home_view

urlpatterns = [
    path('registro/', registro_residente_view, name='registro'),
    path('login/', login_view, name='login'),
    path('home/', home_view, name='home'),
]