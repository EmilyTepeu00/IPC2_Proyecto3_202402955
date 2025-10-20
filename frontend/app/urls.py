from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('enviar-configuracion/', views.enviar_configuracion, name='enviar_configuracion'),
    path('enviar-consumo/', views.enviar_consumo, name='enviar_consumo'),
    path('inicializar-sistema/', views.inicializar_sistema, name='inicializar_sistema'),
]