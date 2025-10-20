from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
import os
import re
from datetime import datetime

#CREAR LA APLICACION Flask
app = Flask(__name__)

#CONFIGURACION DE ARCHIVOS XML
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

ARCHIVO_RECURSOS = os.path.join(DATA_DIR, 'recursos.xml')
ARCHIVO_CATEGORIAS = os.path.join(DATA_DIR, 'categorias.xml')
ARCHIVO_CLIENTES = os.path.join(DATA_DIR, 'clientes.xml')
ARCHIVO_CONFIGURACIONES = os.path.join(DATA_DIR, 'configuraciones.xml')
ARCHIVO_INSTANCIAS = os.path.join(DATA_DIR, 'instancias.xml')

#CREAR ARCHIVOS XML BASE SI NO EXISTEN
def inicializar_archivos_xml():
    archivos_config = {
        ARCHIVO_RECURSOS: 'recursos',
        ARCHIVO_CATEGORIAS: 'categorias',
        ARCHIVO_CLIENTES: 'clientes',
        ARCHIVO_CONFIGURACIONES: 'configuraciones', 
        ARCHIVO_INSTANCIAS: 'instancias'
    }

    for archivo, tag_raiz in archivos_config.items():
        if not os.path.exists(archivo):
            root = ET.Element(tag_raiz)
            tree = ET.ElementTree(root)
            tree.write(archivo, encoding='utf-8', xml_declaration=True)


#CLASE PARA VALIDACIONES CON EXPRESIONES REGULARES
class Validador:
    @staticmethod
    #Validar formato de NIT
    def validar_nit(nit):
        patron = r'^\d+-[0-9K]$'
        return re.match(patron, nit) is not None
    
    @staticmethod
    #Extraer fecha de un texto
    def extraer_fecha(texto):
        patron = r'\b(\d{2}/\d{2}/\d{4})\b'
        coincidencias = re.findall(patron, texto)
        return coincidencias[0] if coincidencias else None


##RUTA PARA RECIBIR MENSAJES DE CONFIGURACION
@app.route('/api/configuracion', methods=['POST'])
def recibir_configuracion():
    """
    Endpoint para recibir mensajes XML de configuracion
    """
    try:
        xml_data = request.data.decode('utf-8')
        
        #Parsear el XML
        root = ET.fromstring(xml_data)
        
        #Contadores para los resultados
        resultados = {
            'recursos_nuevos': 0,
            'categorias_nuevas': 0,
            'clientes_nuevos': 0,
            'configuraciones_nuevas': 0,
            'instancias_nuevas': 0
        }
        
        #Procesar lista de recursos
        lista_recursos = root.find('listaRecursos')
        if lista_recursos is not None:
            for recurso_elem in lista_recursos.findall('recurso'):
                recurso_id = recurso_elem.get('id')
                nombre = recurso_elem.find('nombre').text.strip()
                tipo = recurso_elem.find('tipo').text
                valor_hora = recurso_elem.find('valorXhora').text
                
                print(f"Recurso encontrado: {nombre} (ID: {recurso_id})")
                resultados['recursos_nuevos'] += 1
        
        #Procesar lista de categorias
        lista_categorias = root.find('listaCategorias')
        if lista_categorias is not None:
            for categoria_elem in lista_categorias.findall('categoria'):
                categoria_id = categoria_elem.get('id')
                nombre = categoria_elem.find('nombre').text.strip()
                
                print(f"Categoria encontrada: {nombre} (ID: {categoria_id})")
                resultados['categorias_nuevas'] += 1
        
        #Procesar lista de clientes
        lista_clientes = root.find('listaClientes')
        if lista_clientes is not None:
            for cliente_elem in lista_clientes.findall('cliente'):
                nit = cliente_elem.get('nit')
                nombre = cliente_elem.find('nombre').text.strip()
                
                #Validar NIT con expresion regular
                if Validador.validar_nit(nit):
                    print(f"Cliente valido: {nombre} (NIT: {nit})")
                    resultados['clientes_nuevos'] += 1
                else:
                    print(f"Cliente con NIT invalido: {nit}")
        
        return jsonify({
            "estado": "exito",
            "mensaje": "XML de configuracion procesado correctamente",
            "resultados": resultados
        })
        
    except ET.ParseError as e:
        return jsonify({
            "estado": "error",
            "mensaje": f"XML mal formado: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "estado": "error",
            "mensaje": f"Error al procesar configuracion: {str(e)}"
        }), 400
    
#Ruta basica para probar que la API funcione
@app.route('/')
def hola_mundo():
    return jsonify({"mensaje": "API funcionando", "estado": "OK"})

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
        return jsonify({"estado": "error", "mensaje": f"Error: {str(e)}"}), 400

#RUTA PARA RESETEAR DATOS
@app.route('/api/reset', methods=['POST'])
def resetear_datos():
    """
    Endpoint para eliminar todos los datos (inicializar sistema)
    """
    try:
        inicializar_archivos_xml()
        return jsonify({"estado": "exito", "mensaje": "Sistema inicializado"})
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error: {str(e)}"}), 400
    

if __name__ == '__main__':
    #Ejecutar la aplicacion Flask
    inicializar_archivos_xml()
    app.run(debug=True, port=5000)