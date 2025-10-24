from django.shortcuts import render
from django.http import JsonResponse
import requests
import os
from frontend.settings import BACKEND_URL

#VISTA PRINCIPAL
def index(request):
    return render(request, 'index.html')

#VISTA PARA ENVIAR MENSAJES DE CONFIGURACION
def enviar_configuracion(request):
    if request.method == 'POST' and request.FILES.get('archivo_xml'):
        try:
            #Obtener el archivo XML subido
            archivo_xml = request.FILES['archivo_xml']
            xml_content = archivo_xml.read().decode('utf-8')
            
            #Enviar al backend Flask
            response = requests.post(
                f"{BACKEND_URL}/api/configuracion",
                data=xml_content,
                headers={'Content-Type': 'application/xml'}
            )
            
            return JsonResponse(response.json())
            
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al procesar el archivo: {str(e)}"
            })
    
    #GET: Mostrar formulario subido
    return render(request, 'enviar_configuracion.html')

#VISTA PARA ENVIAR MENSAJES DE CONSUMO
def enviar_consumo(request):
    if request.method == 'POST' and request.FILES.get('archivo_xml'):
        try:
            archivo_xml = request.FILES['archivo_xml']
            xml_content = archivo_xml.read().decode('utf-8')
            
            response = requests.post(
                f"{BACKEND_URL}/api/consumo",
                data=xml_content,
                headers={'Content-Type': 'application/xml'}
            )
            
            return JsonResponse(response.json())
            
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al procesar el archivo: {str(e)}"
            })
    
    #GET: Mostrar formulario
    return render(request, 'enviar_consumo.html')

#VISTA PARA INICIALIZAR/RESETEAR EL SISTEMA
def inicializar_sistema(request):
    if request.method == 'POST':
        try:
            #Llamar a la API del backend para resetear
            response = requests.post(f"{BACKEND_URL}/api/reset")
            return JsonResponse(response.json())
        
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"No se pudo conectar al backend: {str(e)}"
            })
    
    return JsonResponse({"mensaje": "Use POST para inicializar el sistema"})

#VISTA PARA CONSULTAR DATOS DEL SISTEMA
def consultar_datos(request):
    try:
        #Obtener todos los datos del backend
        response = requests.get(f"{BACKEND_URL}/api/consultar/todo")

        if response.status_code == 200:
            datos = response.json()['datos']
        else:
            datos = {
                'recursos': [],
                'categorias': [],
                'clientes': [],
                'configuraciones': [],
                'instancias': [],
                'consumos': []
            }
        
        return render(request, 'consultar_datos.html', {'datos': datos})
        
    except Exception as e:
        return render(request, 'consultar_datos.html', {
            'error': f"No se pudo conectar al backend: {str(e)}",
            'datos': {}
        })

#VISTA PARA CREACION DE NUEVOS DATOS
def crear_datos(request):
    return render(request, 'crear_datos.html')

#VISTA PARA PROCESO DE FACTURACION
def proceso_facturacion(request):
    if request.method == 'POST':
        try:
            data = {
                'fecha_inicio': request.POST.get('fecha_inicio'),
                'fecha_fin': request.POST.get('fecha_fin')
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/facturacion/generar",
                json=data
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Error en el servidor"
                })
                
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al generar facturas: {str(e)}"
            })
    
    #GET: Mostrar formulario
    return render(request, 'proceso_facturacion.html')

#VISTA PARA GENERACION DE REPORTES
def reportes_pdf(request):
    return render(request, 'reportes_pdf.html')

#VISTA DE AYUDA
def ayuda(request):
    info_estudiante = {
        'nombre': 'Emily Maritza Tepeu Guacamaya',
        'carnet': '202402955',
        'curso': 'Introducción a la Programación y Computación 2'
    }
    return render(request, 'ayuda.html', {'estudiante': info_estudiante})