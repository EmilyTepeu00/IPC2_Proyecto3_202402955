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
ARCHIVO_INSTANCIAS = os.path.join(DATA_DIR, 'instancias.xml')

#CREAR ARCHIVOS XML BASE SI NO EXISTEN
def inicializar_archivos_xml():
    archivos_config = {
        ARCHIVO_RECURSOS: 'recursos',
        ARCHIVO_CATEGORIAS: 'categorias', 
        ARCHIVO_CLIENTES: 'clientes',
        ARCHIVO_INSTANCIAS: 'instancias'
    }

    for archivo, tag_raiz in archivos_config.items():
        if not os.path.exists(archivo):
            root = ET.Element(tag_raiz)
            tree = ET.ElementTree(root)
            tree.write(archivo, encoding='utf-8', xml_declaration=True)


#CLASE PARA VALIDACIONES CON EXPRESIONES REGULARES
class Validador:
    
    #Validar formato de NIT
    @staticmethod
    def validar_nit(nit):
        patron = r'^\d+-[0-9K]$'
        return re.match(patron, nit) is not None
    
    #Extraer fecha de un texto
    @staticmethod
    def extraer_fecha(texto):
        patron = r'\b(\d{2}/\d{2}/\d{4})\b'
        coincidencias = re.findall(patron, texto)
        return coincidencias[0] if coincidencias else None
    
    #Validar estado: vigente o cancelado
    @staticmethod
    def validar_estado_instancia(estado):
        return estado in ["Vigente", "Cancelada"]
    
    #Validar tipo de recurso: hardware o software
    @staticmethod
    def validar_tipo_recurso(tipo):
        return tipo in ["Hardware", "Software"]


#RUTA PARA RECIBIR MENSAJES DE CONFIGURACION
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
            'instancias_nuevas': 0,
            'errores': []
        }
        
        #Procesar lista de recursos
        lista_recursos = root.find('listaRecursos')
        if lista_recursos is not None:
            for recurso_elem in lista_recursos.findall('recurso'):
                recurso_id = recurso_elem.get('id')
                nombre = recurso_elem.find('nombre').text.strip()
                tipo = recurso_elem.find('tipo').text
                
                if Validador.validar_tipo_recurso(tipo):
                    print(f"Recurso valido: {nombre} ({tipo})")
                    resultados['recursos_nuevos'] += 1
                else:
                    error_msg = f"Tipo de recurso invalido: {tipo}"
                    print(f"{error_msg}")
                    resultados['errores'].append(error_msg)
        
        #Procesar lista de categorias
        lista_categorias = root.find('listaCategorias')
        if lista_categorias is not None:
            for categoria_elem in lista_categorias.findall('categoria'):
                categoria_id = categoria_elem.get('id')
                nombre = categoria_elem.find('nombre').text.strip()
                print(f"Categoria: {nombre}")
                resultados['categorias_nuevas'] += 1
                
                #Procesar configuraciones dentro de la categoria
                lista_configuraciones = categoria_elem.find('listaConfiguraciones')
                if lista_configuraciones is not None:
                    for config_elem in lista_configuraciones.findall('configuracion'):
                        config_id = config_elem.get('id')
                        config_nombre = config_elem.find('nombre').text.strip()
                        print(f"Configuracion: {config_nombre}")
                        resultados['configuraciones_nuevas'] += 1
        
        #Procesar lista de clientes con NIT
        lista_clientes = root.find('listaClientes')
        if lista_clientes is not None:
            for cliente_elem in lista_clientes.findall('cliente'):
                nit = cliente_elem.get('nit')
                nombre = cliente_elem.find('nombre').text.strip()
                
                #Validar NIT con expresion regular
                if Validador.validar_nit(nit):
                    print(f"Cliente valido: {nombre} (NIT: {nit})")
                    resultados['clientes_nuevos'] += 1

                    #Procesar instancias del cliente
                    lista_instancias = cliente_elem.find('listaInstancias')
                    if lista_instancias is not None:
                        for instancia_elem in lista_instancias.findall('instancia'):
                            instancia_id = instancia_elem.get('id')
                            instancia_nombre = instancia_elem.find('nombre').text.strip()
                            estado = instancia_elem.find('estado').text
                            fecha_inicio = instancia_elem.find('fechaInicio').text
                            
                            #Extraer fecha
                            fecha_extraida = Validador.extraer_fecha(fecha_inicio)
                            
                            if Validador.validar_estado_instancia(estado):
                                print(f"Instancia: {instancia_nombre} ({estado}) - Fecha: {fecha_extraida}")
                                resultados['instancias_nuevas'] += 1
                            else:
                                error_msg = f"Estado de instancia invalido: {estado}"
                                resultados['errores'].append(error_msg)
                else:
                    error_msg = f"NIT invalido: {nit}"
                    print(f"{error_msg}")
                    resultados['errores'].append(error_msg)
        
        return jsonify({
            "estado": "exito",
            "mensaje": "XML procesado con validaciones regex",
            "resultados": resultados
        })
        
    except ET.ParseError as e:
        return jsonify({"estado": "error", "mensaje": f"XML mal formado: {str(e)}"}), 400
    
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error: {str(e)}"}), 400
    
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
        xml_data = request.data.decode('utf-8')
        root = ET.fromstring(xml_data)
        
        consumos_procesados = 0
        errores_consumo = []
        
        for consumo_elem in root.findall('consumo'):
            nit_cliente = consumo_elem.get('nitCliente')
            id_instancia = consumo_elem.get('idInstancia')
            tiempo = consumo_elem.find('tiempo').text
            fecha_hora = consumo_elem.find('fechahora').text
            
            #Extraer fecha/hora
            fecha_hora_extraida = Validador.extraer_fecha_hora(fecha_hora)
            
            if fecha_hora_extraida:
                print(f"Consumo: Instancia {id_instancia}, Tiempo: {tiempo}h, Fecha: {fecha_hora_extraida}")
                consumos_procesados += 1
            else:
                error_msg = f"No se pudo extraer fecha/hora: {fecha_hora}"
                errores_consumo.append(error_msg)
        
        return jsonify({
            "estado": "exito",
            "mensaje": f"Procesados {consumos_procesados} consumos",
            "consumos_procesados": consumos_procesados,
            "errores": errores_consumo
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