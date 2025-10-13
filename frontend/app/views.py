from django.shortcuts import render
from django.http import JsonResponse
import requests
from frontend.settings import BACKEND_URL

#VISTA PRINCIPAL
def index(request):
    return render(request, 'index.html')

#VISTA PARA ENVIAR MENSAJES DE CONFIGURACION
def enviar_configuracion(request):
    if request.method == 'POST':
        try:
            return JsonResponse({
                "estado": "exito",
                "mensaje": "Funcion de enviar configuracioooooon"
            })
        except Exception as e:
            return JsonResponse({
                "estado": "error", 
                "mensaje": str(e)
            })
    
    #Si es GET, se muestra el formulario
    return render(request, 'enviar_configuracion.html')

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
    
    return JsonResponse({"mensaje": "Usa POST para inicializar el sistema"})