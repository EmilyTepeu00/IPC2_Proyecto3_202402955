import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
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

# =============================================
# VISTAS PARA CREACIÓN DE DATOS INDIVIDUALES
# =============================================

def crear_recurso(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar datos del recurso
            if not all(key in data for key in ['id', 'nombre', 'abreviatura', 'metrica', 'tipo', 'valorXhora']):
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Faltan campos obligatorios para el recurso"
                })
            
            # Enviar al backend Flask
            response = requests.post(
                f"{BACKEND_URL}/api/crear/recurso",
                json=data
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Error en el servidor backend"
                })
                
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al crear recurso: {str(e)}"
            })
    
    return JsonResponse({"estado": "error", "mensaje": "Método no permitido"})

def crear_categoria(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar datos de la categoría
            if not all(key in data for key in ['id', 'nombre', 'descripcion', 'cargaTrabajo']):
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Faltan campos obligatorios para la categoría"
                })
            
            # Enviar al backend Flask
            response = requests.post(
                f"{BACKEND_URL}/api/crear/categoria",
                json=data
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Error en el servidor backend"
                })
                
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al crear categoría: {str(e)}"
            })
    
    return JsonResponse({"estado": "error", "mensaje": "Método no permitido"})

def crear_configuracion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar datos de la configuración
            if not all(key in data for key in ['id', 'idCategoria', 'nombre', 'descripcion', 'recursos']):
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Faltan campos obligatorios para la configuración"
                })
            
            # Enviar al backend Flask
            response = requests.post(
                f"{BACKEND_URL}/api/crear/configuracion",
                json=data
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Error en el servidor backend"
                })
                
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al crear configuración: {str(e)}"
            })
    
    return JsonResponse({"estado": "error", "mensaje": "Método no permitido"})

def crear_cliente(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar datos del cliente
            if not all(key in data for key in ['nit', 'nombre', 'usuario', 'clave', 'direccion', 'correoElectronico']):
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Faltan campos obligatorios para el cliente"
                })
            
            # Enviar al backend Flask
            response = requests.post(
                f"{BACKEND_URL}/api/crear/cliente",
                json=data
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Error en el servidor backend"
                })
                
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al crear cliente: {str(e)}"
            })
    
    return JsonResponse({"estado": "error", "mensaje": "Método no permitido"})

def crear_instancia(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar datos de la instancia
            if not all(key in data for key in ['id', 'nitCliente', 'idConfiguracion', 'nombre', 'fechaInicio', 'estado']):
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Faltan campos obligatorios para la instancia"
                })
            
            # Enviar al backend Flask
            response = requests.post(
                f"{BACKEND_URL}/api/crear/instancia",
                json=data
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Error en el servidor backend"
                })
                
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al crear instancia: {str(e)}"
            })
    
    return JsonResponse({"estado": "error", "mensaje": "Método no permitido"})

def crear_consumo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar datos del consumo
            if not all(key in data for key in ['nitCliente', 'idInstancia', 'tiempo', 'fechahora']):
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Faltan campos obligatorios para el consumo"
                })
            
            # Enviar al backend Flask
            response = requests.post(
                f"{BACKEND_URL}/api/crear/consumo",
                json=data
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Error en el servidor backend"
                })
                
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al crear consumo: {str(e)}"
            })
    
    return JsonResponse({"estado": "error", "mensaje": "Método no permitido"})

#VISTA PARA PROCESO DE FACTURACION
def proceso_facturacion(request):
    if request.method == 'POST':
        try:
            # Verificar si es una solicitud de PDF
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                if data.get('action') == 'generar_pdf':
                    numero_factura = data.get('numero_factura')
                    
                    # Llamar al backend Flask para generar PDF
                    response = requests.post(
                        f"{BACKEND_URL}/api/reportes/factura",
                        json={'numero_factura': numero_factura}
                    )
                    
                    if response.status_code == 200:
                        return JsonResponse(response.json())
                    else:
                        return JsonResponse({
                            "estado": "error",
                            "mensaje": "Error generando PDF"
                        })
            
            # Si no es PDF, es facturación normal
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            
            print(f"Procesando facturación: {fecha_inicio} a {fecha_fin}")
            
            data = {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
            
            # Llamar al backend Flask
            response = requests.post(
                f"{BACKEND_URL}/api/facturacion/generar",
                json=data
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    "estado": "error",
                    "mensaje": "Error en el servidor Flask"
                })
                
        except Exception as e:
            return JsonResponse({
                "estado": "error",
                "mensaje": f"Error al generar facturas: {str(e)}"
            })
    
    # GET: Mostrar formulario
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
