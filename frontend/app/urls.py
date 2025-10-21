from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    #OPERACIONES PRINCIPALES DEL SISTEMA
    path('enviar-configuracion/', views.enviar_configuracion, name='enviar_configuracion'),
    path('enviar-consumo/', views.enviar_consumo, name='enviar_consumo'),
    path('inicializar-sistema/', views.inicializar_sistema, name='inicializar_sistema'),
    path('consultar-datos/', views.consultar_datos, name='consultar_datos'),
    path('crear-datos/', views.crear_datos, name='crear_datos'),
    path('proceso-facturacion/', views.proceso_facturacion, name='proceso_facturacion'),
    path('reportes-pdf/', views.reportes_pdf, name='reportes_pdf'),
    path('ayuda/', views.ayuda, name='ayuda'),
]