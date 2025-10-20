from flask import Flask, request, jsonify
import os

#CREAR LA APLICACION Flask
app = Flask(__name__)

#Ruta basica para probar que la API funcione
@app.route('/')
def hola_mundo():
    return jsonify({
        "mensaje": "API de Tecnologias Chapinas, S.A. funcionando",
        "estado": "OK"
    })

##RUTA PARA RECIBIR MENSAJES DE CONFIGURACION
@app.route('/api/configuracion', methods=['POST'])
def recibir_configuracion():
    """
    Endpoint para recibir mensajes XML de configuracion
    """
    try:
        return jsonify({
            "estado": "exito",
            "mensaje": "Mensaje de configuracion recibido correctamente",
            "datos_recibidos": "Procesamientooooooooooooo del xml"
        })
    except Exception as e:
        return jsonify({
            "estado": "error",
            "mensaje": f"Error al procesar configuracion: {str(e)}"
        }), 400

#RUTA PARA RECIBIR MENSAJES DE CONSUMO
@app.route('/api/consumo', methods=['POST'])
def recibir_consumo():
    """
    Endpoint para recibir mensajes XML de consumo
    """
    try:
        return jsonify({
            "estado": "exito",
            "mensaje": "Mensaje de consumo recibido correctamente", 
            "datos_recibidos": "Procesamientoooooooooooooo del XML"
        })
    except Exception as e:
        return jsonify({
            "estado": "error",
            "mensaje": f"Error al procesar consumo: {str(e)}"
        }), 400

#RUTA PARA RESETEAR DATOS
@app.route('/api/reset', methods=['POST'])
def resetear_datos():
    """
    Endpoint para eliminar todos los datos (inicializar sistema)
    """
    try:
        return jsonify({
            "estado": "exito", 
            "mensaje": "Sistema inicializado correctamente"
        })
    except Exception as e:
        return jsonify({
            "estado": "error",
            "mensaje": f"Error al resetear: {str(e)}"
        }), 400
    

if __name__ == '__main__':
    #Ejecutar la aplicacion Flask
    app.run(debug=True, port=5000)