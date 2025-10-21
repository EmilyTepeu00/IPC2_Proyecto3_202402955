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
ARCHIVO_CONSUMOS = os.path.join(DATA_DIR, 'consumos.xml')

#CREAR ARCHIVOS XML BASE SI NO EXISTEN
def inicializar_archivos_xml():
    archivos_config = {
        ARCHIVO_RECURSOS: 'recursos',
        ARCHIVO_CATEGORIAS: 'categorias', 
        ARCHIVO_CLIENTES: 'clientes',
        ARCHIVO_CONFIGURACIONES: 'configuraciones',
        ARCHIVO_INSTANCIAS: 'instancias',
        ARCHIVO_CONSUMOS: 'consumos'
    }

    for archivo, tag_raiz in archivos_config.items():
        if not os.path.exists(archivo):
            root = ET.Element(tag_raiz)
            tree = ET.ElementTree(root)
            tree.write(archivo, encoding='utf-8', xml_declaration=True)

#VERIFICAR SI UN ELEMENTO YA EXISTE EN EL XML
def elemento_existe(archivo, atributo, valor):
    try:
        tree = ET.parse(archivo)
        root = tree.getroot()
        return root.find(f".//*[@{atributo}='{valor}']") is not None
    except:
        return False
    
#AGREGAR UN RECURSO AL XML
def agregar_recurso(recurso_data):
    try:
        tree = ET.parse(ARCHIVO_RECURSOS)
        root = tree.getroot()

        #Verificar si ya existe
        if elemento_existe(ARCHIVO_RECURSOS, 'id', recurso_data['id']):
            return False
        
        #Crear elemento recuros
        recurso_elem = ET.Element('recurso')
        recurso_elem.set('id', recurso_data['id'])

        ET.SubElement(recurso_elem, 'nombre').text = recurso_data['nombre']
        ET.SubElement(recurso_elem, 'abreviatura').text = recurso_data['abreviatura']
        ET.SubElement(recurso_elem, 'metrica').text = recurso_data['metrica']
        ET.SubElement(recurso_elem, 'tipo').text = recurso_data['tipo']
        ET.SubElement(recurso_elem, 'valorXhora').text = str(recurso_data['valorXhora'])

        root.append(recurso_elem)
        tree.write(ARCHIVO_RECURSOS, encoding='utf-8', xml_declaration=True)
        return True
    
    except Exception as e:
        print(f"Error guardando recurso: {e}")
        return False
    
#AGREGAR UNA CATEGORIA AL XML
def agregar_categoria(categoria_data):
    try:
        tree = ET.parse(ARCHIVO_CATEGORIAS)
        root = tree.getroot()

        if elemento_existe(ARCHIVO_CATEGORIAS, 'id', categoria_data['id']):
            return False
        
        categoria_elem = ET.Element('categoria')
        categoria_elem.set('id', categoria_data['id'])

        ET.SubElement(categoria_elem, 'nombre').text = categoria_data['nombre']
        ET.SubElement(categoria_elem, 'description').text = categoria_data['descripcion']
        ET.SubElement(categoria_elem, 'cargaTrabajo').text = categoria_data['cargaTrabajo']

        #Agregar lista de configuraciones vacia
        lista_config = ET.SubElement(categoria_elem, 'listaConfiguraciones')
        
        root.append(categoria_elem)
        tree.write(ARCHIVO_CATEGORIAS, encoding='utf-8', xml_declaration=True)
        return True
    
    except Exception as e:
        print(f"Error guardando categoria: {e}")
        return False
    
#AGREGAR UN CLIENTE AL XML
def agregar_cliente(cliente_data):
    try:
        tree = ET.parse(ARCHIVO_CLIENTES)
        root = tree.getroot()
        
        if elemento_existe(ARCHIVO_CLIENTES, 'nit', cliente_data['nit']):
            return False
        
        cliente_elem = ET.Element('cliente')
        cliente_elem.set('nit', cliente_data['nit'])
        
        ET.SubElement(cliente_elem, 'nombre').text = cliente_data['nombre']
        ET.SubElement(cliente_elem, 'usuario').text = cliente_data['usuario']
        ET.SubElement(cliente_elem, 'clave').text = cliente_data['clave']
        ET.SubElement(cliente_elem, 'direccion').text = cliente_data['direccion']
        ET.SubElement(cliente_elem, 'correoElectronico').text = cliente_data['correoElectronico']

        #Agregar lista de instancias vacia
        lista_instancias = ET.SubElement(cliente_elem, 'listaInstancias')

        lista_instancias = ET.SubElement(cliente_elem, 'listaInstancias')
        
        root.append(cliente_elem)
        tree.write(ARCHIVO_CLIENTES, encoding='utf-8', xml_declaration=True)
        return True
    
    except Exception as e:
        print(f"Error guardando cliente: {e}")
        return False
 
#AGREGAR UNA CONFIGURACION AL XML
def agregar_configuracion(config_data):
    try:
        tree = ET.parse(ARCHIVO_CONFIGURACIONES)
        root = tree.getroot()
        
        if elemento_existe(ARCHIVO_CONFIGURACIONES, 'id', config_data['id']):
            return False
        
        config_elem = ET.Element('configuracion')
        config_elem.set('id', config_data['id'])
        config_elem.set('idCategoria', config_data['idCategoria'])
        
        ET.SubElement(config_elem, 'nombre').text = config_data['nombre']
        ET.SubElement(config_elem, 'description').text = config_data['descripcion']

        #Agregar recursos de la configuracion
        recursos_config = ET.SubElement(config_elem, 'recursosConfiguracion')
        for recurso_id, cantidad in config_data['recursos'].items():
            recurso_elem = ET.SubElement(recursos_config, 'recurso')
            recurso_elem.set('id', recurso_id)
            recurso_elem.text = str(cantidad)

        root.append(config_elem)
        tree.write(ARCHIVO_CONFIGURACIONES, encoding='utf-8', xml_declaration=True)
        return True
    
    except Exception as e:
        print(f"Error guardando configuracion: {e}")
        return False
    
#AGREGAR UNA INSTANCIA AL XML
def agregar_instancia(instancia_data):
    try:
        tree = ET.parse(ARCHIVO_INSTANCIAS)
        root = tree.getroot()
        
        if elemento_existe(ARCHIVO_INSTANCIAS, 'id', instancia_data['id']):
            return False
        
        instancia_elem = ET.Element('instancia')
        instancia_elem.set('id', instancia_data['id'])
        instancia_elem.set('nitCliente', instancia_data['nitCliente'])

        ET.SubElement(instancia_elem, 'idConfiguracion').text = instancia_data['idConfiguracion']
        ET.SubElement(instancia_elem, 'nombre').text = instancia_data['nombre']
        ET.SubElement(instancia_elem, 'fechaInicio').text = instancia_data['fechaInicio']
        ET.SubElement(instancia_elem, 'estado').text = instancia_data['estado']

        if instancia_data.get('fechaFinal'):
            ET.SubElement(instancia_elem, 'fechaFinal').text = instancia_data['fechaFinal']
        
        root.append(instancia_elem)
        tree.write(ARCHIVO_INSTANCIAS, encoding='utf-8', xml_declaration=True)
        return True

    except Exception as e:
        print(f"Error guardando instancia: {e}")
        return False
    
#AGREGAR UN CONSUMO AL XML
def agregar_consumo(consumo_data):
    try:
        tree = ET.parse(ARCHIVO_CONSUMOS)
        root = tree.getroot()
        
        consumo_elem = ET.Element('consumo')
        consumo_elem.set('nitCliente', consumo_data['nitCliente'])
        consumo_elem.set('idInstancia', consumo_data['idInstancia'])
        
        ET.SubElement(consumo_elem, 'tiempo').text = str(consumo_data['tiempo'])
        ET.SubElement(consumo_elem, 'fechahora').text = consumo_data['fechahora']

        root.append(consumo_elem)
        tree.write(ARCHIVO_CONSUMOS, encoding='utf-8', xml_declaration=True)
        return True
    
    except Exception as e:
        print(f"Error guardando consumo: {e}")
        return False

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
    
    #Extraer fecha y hora
    @staticmethod
    def extraer_fecha_hora(texto):
        patron = r'\b(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\b'
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
            'recursos_guardados': 0,
            'categorias_guardadas': 0, 
            'clientes_guardados': 0,
            'configuraciones_guardadas': 0,
            'instancias_guardadas': 0,
            'errores': []
        }
        
        #Procesar  y guardar recursos
        lista_recursos = root.find('listaRecursos')
        if lista_recursos is not None:
            for recurso_elem in lista_recursos.findall('recurso'):
                recurso_data = {
                    'id': recurso_elem.get('id'),
                    'nombre': recurso_elem.find('nombre').text.strip(),
                    'abreviatura': recurso_elem.find('abreviatura').text.strip(),
                    'metrica': recurso_elem.find('metrica').text.strip(),
                    'tipo': recurso_elem.find('tipo').text,
                    'valorXhora': float(recurso_elem.find('valorXhora').text)
                }
                
                if Validador.validar_tipo_recurso(recurso_data['tipo']):
                    if agregar_recurso(recurso_data):
                        print(f"Recurso guardado: {recurso_data['nombre']}")
                        resultados['recursos_guardados'] += 1
                    else:
                        print(f"Recurso ya existe: {recurso_data['nombre']}")
                else:
                    error_msg = f"Tipo de recurso invalido: {recurso_data['tipo']}"
                    resultados['errores'].append(error_msg)
        
        #Procesar y guardar categorias
        lista_categorias = root.find('listaCategorias')
        if lista_categorias is not None:
            for categoria_elem in lista_categorias.findall('categoria'):
                categoria_data = {
                    'id': categoria_elem.get('id'),
                    'nombre': categoria_elem.find('nombre').text.strip(),
                    'descripcion': categoria_elem.find('description').text.strip(),
                    'cargaTrabajo': categoria_elem.find('cargaTrabajo').text.strip()
                }
                
                if agregar_categoria(categoria_data):
                    print(f"Categoria guardada: {categoria_data['nombre']}")
                    resultados['categorias_guardadas'] += 1
                
                #Procesar configuraciones de la categoria
                lista_configuraciones = categoria_elem.find('listaConfiguraciones')
                if lista_configuraciones is not None:
                    for config_elem in lista_configuraciones.findall('configuracion'):
                        config_data = {
                            'id': config_elem.get('id'),
                            'idCategoria': categoria_data['id'],
                            'nombre': config_elem.find('nombre').text.strip(),
                            'descripcion': config_elem.find('description').text.strip(),
                            'recursos': {}
                        }
                        
                        #Procesar recursos de la configuracion
                        recursos_config = config_elem.find('recursosConfiguracion')
                        if recursos_config is not None:
                            for recurso_config in recursos_config.findall('recurso'):
                                recurso_id = recurso_config.get('id')
                                cantidad = float(recurso_config.text)
                                config_data['recursos'][recurso_id] = cantidad
                        
                        if agregar_configuracion(config_data):
                            print(f"Configuracion guardada: {config_data['nombre']}")
                            resultados['configuraciones_guardadas'] += 1
        
        #Procesar y guardar clientes
        lista_clientes = root.find('listaClientes')
        if lista_clientes is not None:
            for cliente_elem in lista_clientes.findall('cliente'):
                nit = cliente_elem.get('nit')
                
                #Validar NIT con expresion regular
                if Validador.validar_nit(nit):
                    cliente_data = {
                        'nit': nit,
                        'nombre': cliente_elem.find('nombre').text.strip(),
                        'usuario': cliente_elem.find('usuario').text.strip(),
                        'clave': cliente_elem.find('clave').text.strip(),
                        'direccion': cliente_elem.find('direccion').text.strip(),
                        'correoElectronico': cliente_elem.find('correoElectronico').text.strip()
                    }

                    if agregar_cliente(cliente_data):
                        print(f"Cliente guardado: {cliente_data['nombre']}")
                        resultados['clientes_guardados'] += 1

                    #Procesar instancias del cliente
                    lista_instancias = cliente_elem.find('listaInstancias')
                    if lista_instancias is not None:
                        for instancia_elem in lista_instancias.findall('instancia'):
                            fecha_inicio = instancia_elem.find('fechaInicio').text
                            fecha_extraida = Validador.extraer_fecha(fecha_inicio)
                            
                            instancia_data = {
                                'id': instancia_elem.get('id'),
                                'nitCliente': nit,
                                'idConfiguracion': instancia_elem.find('idConfiguracion').text,
                                'nombre': instancia_elem.find('nombre').text.strip(),
                                'fechaInicio': fecha_extraida or fecha_inicio,
                                'estado': instancia_elem.find('estado').text
                            }
                            
                            #Procesar fecha final si hay
                            fecha_final_elem = instancia_elem.find('fechaFinal')
                            if fecha_final_elem is not None:
                                fecha_final_extraida = Validador.extraer_fecha(fecha_final_elem.text)
                                instancia_data['fechaFinal'] = fecha_final_extraida or fecha_final_elem.text
                            
                            if Validador.validar_estado_instancia(instancia_data['estado']):
                                if agregar_instancia(instancia_data):
                                    print(f"Instancia guardada: {instancia_data['nombre']}")
                                    resultados['instancias_guardadas'] += 1
                            else:
                                error_msg = f"Estado de instancia invalido: {instancia_data['estado']}"
                                resultados['errores'].append(error_msg)
                else:
                    error_msg = f"NIT invalido: {nit}"
                    resultados['errores'].append(error_msg)
        
        return jsonify({
            "estado": "exito",
            "mensaje": "Datos guardados en archivo XML",
            "resultados": resultados
        })
        
    except ET.ParseError as e:
        return jsonify({"estado": "error", "mensaje": f"XML mal formado: {str(e)}"}), 400
        
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error: {str(e)}"}), 400
    

#RUTA PARA RECIBIR MENSAJES DE CONSUMO
@app.route('/api/consumo', methods=['POST'])
def recibir_consumo():
    """
    Endpoint para recibir mensajes XML de consumo
    """
    try:
        xml_data = request.data.decode('utf-8')
        root = ET.fromstring(xml_data)
        
        consumos_guardados = 0
        errores_consumo = []
        
        for consumo_elem in root.findall('consumo'):
            nit_cliente = consumo_elem.get('nitCliente')
            id_instancia = consumo_elem.get('idInstancia')
            tiempo = float(consumo_elem.find('tiempo').text)
            fecha_hora = consumo_elem.find('fechahora').text
            
            #Extraer fecha/hora
            fecha_hora_extraida = Validador.extraer_fecha_hora(fecha_hora)
            
            if fecha_hora_extraida:
                consumo_data = {
                    'nitCliente': nit_cliente,
                    'idInstancia': id_instancia,
                    'tiempo': tiempo,
                    'fechahora': fecha_hora_extraida
                }
                
                if agregar_consumo(consumo_data):
                    print(f"Consumo guardado: Instancia {id_instancia}, {tiempo}h")
                    consumos_guardados += 1
            else:
                error_msg = f"No se pudo extraer fecha/hora: {fecha_hora}"
                errores_consumo.append(error_msg)
        
        return jsonify({
            "estado": "exito",
            "mensaje": f"Guardados {consumos_guardados} consumos",
            "consumos_guardados": consumos_guardados,
            "errores": errores_consumo
        })
        
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error: {str(e)}"}), 400
    

#Ruta basica para probar que la API funcione
@app.route('/')
def hola_mundo():
    return jsonify({"mensaje": "API funcionando", "estado": "OK"})

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
    

#Ejecutar la aplicacion Flask
if __name__ == '__main__':
    inicializar_archivos_xml()
    app.run(debug=True, port=5000)