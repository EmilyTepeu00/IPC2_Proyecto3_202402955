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
    
    #RUTAS PARA CREACION DE DATOS
    path('crear-datos/recurso/', views.crear_recurso, name='crear_recurso'),
    path('crear-datos/categoria/', views.crear_categoria, name='crear_categoria'),
    path('crear-datos/configuracion/', views.crear_configuracion, name='crear_configuracion'),
    path('crear-datos/cliente/', views.crear_cliente, name='crear_cliente'),
    path('crear-datos/instancia/', views.crear_instancia, name='crear_instancia'),
    path('crear-datos/consumo/', views.crear_consumo, name='crear_consumo'),
    
    path('proceso-facturacion/', views.proceso_facturacion, name='proceso_facturacion'),
    path('reportes-pdf/', views.reportes_pdf, name='reportes_pdf'),
    path('ayuda/', views.ayuda, name='ayuda'),
]