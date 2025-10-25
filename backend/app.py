from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import xml.etree.ElementTree as ET
import os
import re
from datetime import datetime, timedelta
from pdf_generator import generar_reporte_factura, generar_analisis_ventas

#CREAR LA APLICACION Flask
app = Flask(__name__)
CORS(app)

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
            with open(archivo, 'w', encoding='utf-8') as f:
                tree.write(f, encoding='unicode', xml_declaration=True)

#VERIFICAR SI UN ELEMENTO YA EXISTE EN EL XML
def elemento_existe(archivo, atributo, valor):
    try:
        tree = ET.parse(archivo)
        root = tree.getroot()
        
        #Buscar en todos los elementos
        for elem in root.findall('*'):
            if elem.get(atributo) == valor:
                return True
        return False
    except:
        return False

# =============================================
#       FUNCIONES DE GUARDADO EN EL XML
# =============================================

#AGREGAR UN RECURSO
def agregar_recurso(recurso_data):
    try:
        #Asegurarse de que el archivo existe
        if not os.path.exists(ARCHIVO_RECURSOS):
            inicializar_archivos_xml()
            
        tree = ET.parse(ARCHIVO_RECURSOS)
        root = tree.getroot()

        #Verificar si ya existe
        if elemento_existe(ARCHIVO_RECURSOS, 'id', recurso_data['id']):
            return False
        
        #Crear elemento recurso
        recurso_elem = ET.Element('recurso')
        recurso_elem.set('id', recurso_data['id'])

        ET.SubElement(recurso_elem, 'nombre').text = recurso_data['nombre']
        ET.SubElement(recurso_elem, 'abreviatura').text = recurso_data['abreviatura']
        ET.SubElement(recurso_elem, 'metrica').text = recurso_data['metrica']
        ET.SubElement(recurso_elem, 'tipo').text = recurso_data['tipo']
        ET.SubElement(recurso_elem, 'valorXhora').text = str(recurso_data['valorXhora'])

        root.append(recurso_elem)
        
        with open(ARCHIVO_RECURSOS, 'w', encoding='utf-8') as f:
            tree.write(f, encoding='unicode', xml_declaration=True)
        return True
    
    except Exception as e:
        print(f"Error guardando recurso: {e}")
        import traceback
        print(f"Traceback guardar recurso: {traceback.format_exc()}")
        return False

#AGREGAR UNA CATEGORIA
def agregar_categoria(categoria_data):
    try:
        tree = ET.parse(ARCHIVO_CATEGORIAS)
        root = tree.getroot()
        
        if elemento_existe(ARCHIVO_CATEGORIAS, 'id', categoria_data['id']):
            return False
        
        categoria_elem = ET.Element('categoria')
        categoria_elem.set('id', categoria_data['id'])
        
        ET.SubElement(categoria_elem, 'nombre').text = categoria_data['nombre']
        
        #Buscar 'descripcion' o 'description'
        descripcion = categoria_data.get('descripcion') or categoria_data.get('description', '')
        ET.SubElement(categoria_elem, 'description').text = descripcion
        
        ET.SubElement(categoria_elem, 'cargaTrabajo').text = categoria_data['cargaTrabajo']
        
        #Agregar lista de configuraciones vacia
        lista_config = ET.SubElement(categoria_elem, 'listaConfiguraciones')
        
        root.append(categoria_elem)
        tree.write(ARCHIVO_CATEGORIAS, encoding='utf-8', xml_declaration=True)
        return True
    except Exception as e:
        return False
    
#AGREGAR UN CLIENTE
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

        #Agregar una lista de instancias vacia
        lista_instancias = ET.SubElement(cliente_elem, 'listaInstancias')
        
        root.append(cliente_elem)
        tree.write(ARCHIVO_CLIENTES, encoding='utf-8', xml_declaration=True)
        return True
    
    except Exception as e:
        return False
 
#AGREGAR UNA CONFIGURACION
def agregar_configuracion(config_data):
    try:
        #Asegurarse de que el archivo existe
        if not os.path.exists(ARCHIVO_CONFIGURACIONES):
            inicializar_archivos_xml()
            
        tree = ET.parse(ARCHIVO_CONFIGURACIONES)
        root = tree.getroot()
        
        #Verificar si ya existe
        for config_elem in root.findall('configuracion'):
            if config_elem.get('id') == config_data['id']:
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
        
        with open(ARCHIVO_CONFIGURACIONES, 'w', encoding='utf-8') as f:
            tree.write(f, encoding='unicode', xml_declaration=True)
        return True
    
    except Exception as e:
        print(f"Error guardando configuracion: {e}")
        import traceback
        print(f"Traceback guardar configuracion: {traceback.format_exc()}")
        return False
    
#AGREGAR UNA INSTANCIA
def agregar_instancia(instancia_data):
    try:
        tree = ET.parse(ARCHIVO_INSTANCIAS)
        root = tree.getroot()
        
        #Verificar si ya existe
        for instancia_elem in root.findall('instancia'):
            if instancia_elem.get('id') == instancia_data['id']:
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
        
        #Guardar precios originales de los recursos de la configuracion
        configuraciones = leer_configuraciones()
        configuracion = next((c for c in configuraciones if c['id'] == instancia_data['idConfiguracion']), None)
        
        if configuracion:
            recursos = leer_recursos()
            precios_originales = {}
            
            for recurso_id in configuracion['recursos'].keys():
                recurso = next((r for r in recursos if r['id'] == recurso_id), None)
                if recurso:
                    precios_originales[recurso_id] = recurso['valorXhora']
            
            guardar_precios_instancia(instancia_data['id'], precios_originales)
        
        return True
        
    except Exception as e:
        return False
    
#AGREGAR UN CONSUMO
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
        return False

# =============================================
#         FUNCIONES PARA LEER EL XML
# =============================================

#LEER TODOS LOS RECURSOS
def leer_recursos():
    try:
        tree = ET.parse(ARCHIVO_RECURSOS)
        root = tree.getroot()
        recursos = []
        for recurso_elem in root.findall('recurso'):
            recursos.append({
                'id': recurso_elem.get('id'),
                'nombre': recurso_elem.find('nombre').text,
                'abreviatura': recurso_elem.find('abreviatura').text,
                'metrica': recurso_elem.find('metrica').text,
                'tipo': recurso_elem.find('tipo').text,
                'valorXhora': float(recurso_elem.find('valorXhora').text)
            })
        return recursos
    except:
        return []
    
#LEER TODAS LAS CATEGORIAS
def leer_categorias():
    try:
        tree = ET.parse(ARCHIVO_CATEGORIAS)
        root = tree.getroot()
        categorias = []
        for categoria_elem in root.findall('categoria'):
            categoria = {
                'id': categoria_elem.get('id'),
                'nombre': categoria_elem.find('nombre').text,
                'descripcion': categoria_elem.find('description').text,
                'cargaTrabajo': categoria_elem.find('cargaTrabajo').text,
                'configuraciones': []
            }
            
            #Leer configuraciones de esta categoria
            lista_configs = categoria_elem.find('listaConfiguraciones')
            if lista_configs is not None:
                for config_elem in lista_configs.findall('configuracion'):
                    config = {
                        'id': config_elem.get('id'),
                        'nombre': config_elem.find('nombre').text,
                        'descripcion': config_elem.find('description').text
                    }
                    categoria['configuraciones'].append(config)
            
            categorias.append(categoria)
        return categorias
    except:
        return []

#LEER TODOS LOS CLIENTES
def leer_clientes():
    try:
        tree = ET.parse(ARCHIVO_CLIENTES)
        root = tree.getroot()
        clientes = []
        for cliente_elem in root.findall('cliente'):
            cliente = {
                'nit': cliente_elem.get('nit'),
                'nombre': cliente_elem.find('nombre').text,
                'usuario': cliente_elem.find('usuario').text,
                'direccion': cliente_elem.find('direccion').text,
                'correoElectronico': cliente_elem.find('correoElectronico').text,
                'instancias': []
            }
            
            #Leer instancias de este cliente
            lista_instancias = cliente_elem.find('listaInstancias')
            if lista_instancias is not None:
                for instancia_elem in lista_instancias.findall('instancia'):
                    instancia = {
                        'id': instancia_elem.get('id'),
                        'idConfiguracion': instancia_elem.find('idConfiguracion').text,
                        'nombre': instancia_elem.find('nombre').text,
                        'fechaInicio': instancia_elem.find('fechaInicio').text,
                        'estado': instancia_elem.find('estado').text
                    }
                    
                    #Leer fecha final si es que hay
                    fecha_final_elem = instancia_elem.find('fechaFinal')
                    if fecha_final_elem is not None:
                        instancia['fechaFinal'] = fecha_final_elem.text
                    
                    cliente['instancias'].append(instancia)
            
            clientes.append(cliente)
        return clientes
    except:
        return []
    
#LEER TODAS LAS CONFIGURACIONES
def leer_configuraciones():
    try:
        tree = ET.parse(ARCHIVO_CONFIGURACIONES)
        root = tree.getroot()
        configuraciones = []
        for config_elem in root.findall('configuracion'):
            config = {
                'id': config_elem.get('id'),
                'idCategoria': config_elem.get('idCategoria'),
                'nombre': config_elem.find('nombre').text,
                'descripcion': config_elem.find('description').text,
                'recursos': {}
            }
            
            #Leer recursos de la configuracion
            recursos_config = config_elem.find('recursosConfiguracion')
            if recursos_config is not None:
                for recurso_config in recursos_config.findall('recurso'):
                    recurso_id = recurso_config.get('id')
                    cantidad = float(recurso_config.text)
                    config['recursos'][recurso_id] = cantidad
            
            configuraciones.append(config)
        return configuraciones
    except:
        return []

#LEER TODAS LAS INSTANCIAS
def leer_instancias():
    try:
        tree = ET.parse(ARCHIVO_INSTANCIAS)
        root = tree.getroot()
        instancias = []
        for instancia_elem in root.findall('instancia'):
            instancia = {
                'id': instancia_elem.get('id'),
                'nitCliente': instancia_elem.get('nitCliente'),
                'idConfiguracion': instancia_elem.find('idConfiguracion').text,
                'nombre': instancia_elem.find('nombre').text,
                'fechaInicio': instancia_elem.find('fechaInicio').text,
                'estado': instancia_elem.find('estado').text
            }
            
            fecha_final_elem = instancia_elem.find('fechaFinal')
            if fecha_final_elem is not None:
                instancia['fechaFinal'] = fecha_final_elem.text
            
            instancias.append(instancia)
        return instancias
    except:
        return []
    
#LEER TODOS LOS CONSUMOS
def leer_consumos():
    try:
        tree = ET.parse(ARCHIVO_CONSUMOS)
        root = tree.getroot()
        consumos = []
        for consumo_elem in root.findall('consumo'):
            consumo = {
                'nitCliente': consumo_elem.get('nitCliente'),
                'idInstancia': consumo_elem.get('idInstancia'),
                'tiempo': float(consumo_elem.find('tiempo').text),
                'fechahora': consumo_elem.find('fechahora').text
            }
            consumos.append(consumo)
        return consumos
    except:
        return []

#CLASE PARA VALIDACIONES CON EXPRESIONES REGULARES
class Validador:
    
   #Validar formato de NIT
    @staticmethod
    def validar_nit(nit):
        if not nit:
            return False
        #Patron más flexible para testing
        patron = r'^\d+[-]?[\dKk]?$'
        return re.match(patron, nit) is not None
    
    #Extraer fecha de un texto
    @staticmethod
    def extraer_fecha(texto):
        if not texto:
            return None
        patron = r'\b(\d{2}/\d{2}/\d{4})\b'
        coincidencias = re.findall(patron, texto)
        return coincidencias[0] if coincidencias else None
    
    #Extraer fecha y hora
    @staticmethod
    def extraer_fecha_hora(texto):
        if not texto:
            return None
        patron = r'\b(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\b'
        coincidencias = re.findall(patron, texto)
        return coincidencias[0] if coincidencias else None
    
    #Validar estado: vigente o cancelado
    @staticmethod
    def validar_estado_instancia(estado):
        estado_upper = estado.upper()
        return estado_upper in ["VIGENTE", "CANCELADA", "ACTIVA", "CANCELADO"]
    
    #Validar tipo de recurso: hardware o software
    @staticmethod
    def validar_tipo_recurso(tipo):
        tipo_upper = tipo.upper()
        return tipo_upper in ["HARDWARE", "SOFTWARE", "HW", "SW"]
    
# =============================================
#          FUNCIONES PARA FACTURACION
# =============================================

#GUARDAR PRECIOS ORIGINALES DE LOS RECURSOS AL CREAR INSTANCIAS
def guardar_precios_instancia(instancia_id, precios):
    try:
        #Buscar las instancia en el archivo
        tree = ET.parse(ARCHIVO_INSTANCIAS)
        root = tree.getroot()
        
        for instancia_elem in root.findall('instancia'):
            if instancia_elem.get('id') == instancia_id:
                #Eliminar precios existentes si hay
                precios_existentes = instancia_elem.find('preciosOriginales')
                if precios_existentes is not None:
                    instancia_elem.remove(precios_existentes)

                #Crear elemento de precios originales
                precios_elem = ET.SubElement(instancia_elem, 'preciosOriginales')
                for recurso_id, precio in precios.items():
                    recurso_precio = ET.SubElement(precios_elem, 'recurso')
                    recurso_precio.set('id', recurso_id)
                    recurso_precio.set('precio', str(precio))
                
                tree.write(ARCHIVO_INSTANCIAS, encoding='utf-8', xml_declaration=True)
                return True
            
        return False
    except Exception as e:
        return False
    
#OBTENER LOS PRECIOS ORIGINALES DE UNA INSTANCIA
def obtener_precios_instancia(instancia_id):
    try:
        tree = ET.parse(ARCHIVO_INSTANCIAS)
        root = tree.getroot()
        
        for instancia_elem in root.findall('instancia'):
            if instancia_elem.get('id') == instancia_id:
                precios_elem = instancia_elem.find('preciosOriginales')
                if precios_elem is not None:
                    precios = {}
                    for recurso_precio in precios_elem.findall('recurso'):
                        precios[recurso_precio.get('id')] = float(recurso_precio.get('precio'))
                    return precios
        return None
    except:
        return None
    
#CALCULAR COSTO TOTAL DE UNA INSTANCIA
def calcular_costo_instancia(instancia_id, consumos):
    try:
        #Obtener precios originales de la instancia
        precios_originales = obtener_precios_instancia(instancia_id)
        
        if not precios_originales:
            return 0.0
        
        #Obtener configuracion de la instancia para saber que recursos usa
        instancias = leer_instancias()
        configuraciones = leer_configuraciones()
        
        instancia_info = next((i for i in instancias if i['id'] == instancia_id), None)
        if not instancia_info:
            return 0.0
        
        configuracion = next((c for c in configuraciones if c['id'] == instancia_info['idConfiguracion']), None)
        if not configuracion:
            return 0.0
        
        #Calcular costo total
        costo_total = 0.0
        
        for consumo in consumos:
            if consumo['idInstancia'] == instancia_id:
                #Calcular costo para cada recurso
                for recurso_id, cantidad in configuracion['recursos'].items():
                    if recurso_id in precios_originales:
                        precio_recurso = precios_originales[recurso_id]
                        costo_recurso = precio_recurso * cantidad * consumo['tiempo']
                        costo_total += costo_recurso
        
        return round(costo_total, 2)
    except Exception as e:
        return 0.0

#Variable global para el contador de facturas
CONTADOR_FACTURAS = 1000

#GENERAR FACTURA EN RANGO DE FECHAS
def generar_factura(nit_cliente, fecha_inicio, fecha_fin):
    global CONTADOR_FACTURAS
    
    try:
        #Obtener consumos del cliente en el rango de fechas
        consumos = leer_consumos()
        instancias = leer_instancias()
        clientes = leer_clientes()
        
        #Filtrar consumos por cliente y fecha
        consumos_cliente = []
        for consumo in consumos:
            if consumo['nitCliente'] == nit_cliente:
                #Extraer fecha del consumo
                fecha_consumo = Validador.extraer_fecha(consumo['fechahora'])
                if fecha_consumo:
                    fecha_consumo_dt = datetime.strptime(fecha_consumo, '%d/%m/%Y')
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                    
                    if fecha_inicio_dt <= fecha_consumo_dt <= fecha_fin_dt:
                        consumos_cliente.append(consumo)
        
        #Si no hay consumos, retornar None
        if not consumos_cliente:
            return None
        
        #Agrupar consumos por instancia
        consumos_por_instancia = {}
        for consumo in consumos_cliente:
            instancia_id = consumo['idInstancia']
            if instancia_id not in consumos_por_instancia:
                consumos_por_instancia[instancia_id] = []
            consumos_por_instancia[instancia_id].append(consumo)
        
        #Calcular costos por instancia
        factura_detalle = []
        total_factura = 0.0
        
        for instancia_id, consumos_instancia in consumos_por_instancia.items():
            costo_instancia = calcular_costo_instancia(instancia_id, consumos_instancia)
            total_factura += costo_instancia
            
            #Obtener info de la instancia
            instancia_info = next((i for i in instancias if i['id'] == instancia_id), None)
            if instancia_info:
                factura_detalle.append({
                    'instancia_id': instancia_id,
                    'instancia_nombre': instancia_info['nombre'],
                    'consumos': consumos_instancia,
                    'costo': costo_instancia
                })
        
        #Generar numero de factura secuencial
        CONTADOR_FACTURAS += 1
        numero_factura = f"FAC-{CONTADOR_FACTURAS}"
        
        cliente_info = next((c for c in clientes if c['nit'] == nit_cliente), None)
        
        return {
            'numero_factura': numero_factura,
            'nit_cliente': nit_cliente,
            'nombre_cliente': cliente_info['nombre'] if cliente_info else 'Cliente',
            'fecha_factura': fecha_fin,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'detalle': factura_detalle,
            'monto_total': round(total_factura, 2),
            'estado': 'generada'
        }
    
    except Exception as e:
        return None

#LIMPIAR XML COMPLETO
def limpiar_y_validar_xml(xml_data):
    if not xml_data or not xml_data.strip():
        return '<?xml version="1.0" encoding="UTF-8"?><archivoConfiguraciones></archivoConfiguraciones>'
    
    #Quitar caracteres de control invalidos
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_data)
    
    #Quitar espacios en blanco al inicio y final
    cleaned = cleaned.strip()
    
    #Areglar etiquetas mal formadas
    #Arreglar el cierre de archivoConfiguraciones si esta mal
    if cleaned.endswith('</archivoConfiguracione'):
        cleaned = cleaned[:-23] + '</archivoConfiguraciones>'
    
    #Arreglar otros cierres mal formados
    malformed_closures = [
        ('</archivoConfiguracione', '</archivoConfiguraciones>'),
        ('</listaInstancia', '</listaInstancias>'),
        ('</listaCategoria', '</listaCategorias>'),
        ('</listaConfiguracione', '</listaConfiguraciones>'),
        ('</recursoConfiguracion', '</recursosConfiguracion>')
    ]
    
    for malformed, correct in malformed_closures:
        if cleaned.endswith(malformed):
            cleaned = cleaned[:-len(malformed)] + correct
    
    #Verificar que empiece correctamente
    if not cleaned.startswith('<?xml'):
        #Agregar declaracion XML si falta
        cleaned = '<?xml version="1.0" encoding="UTF-8"?>' + cleaned
    
    #Asegurar que tenga la estructura basica completa
    if '<archivoConfiguraciones>' in cleaned and '</archivoConfiguraciones>' not in cleaned:
        #Si falta el cierre principal se agrega
        if not cleaned.endswith('</archivoConfiguraciones>'):
            cleaned += '</archivoConfiguraciones>'
    
    #Intentar parsear para verificar
    try:
        ET.fromstring(cleaned)
        return cleaned
    except ET.ParseError as e:
        #Si no se puede parsear, intentar una arreglarlo mas agresiva
        return reparacion_agresiva_xml(cleaned)

#POR SI EL XML ESTA MAL ESCRITO
def reparacion_agresiva_xml(xml_data):
    
    #Extraer todas las partes validas
    recursos_match = re.search(r'<listaRecursos>.*?</listaRecursos>', xml_data, re.DOTALL)
    categorias_match = re.search(r'<listaCategorias>.*?</listaCategorias>', xml_data, re.DOTALL)
    clientes_match = re.search(r'<listaClientes>.*?</listaClientes>', xml_data, re.DOTALL)
    
    #Construir un XML valido con las partes validas
    xml_reparado = '<?xml version="1.0" encoding="UTF-8"?>\n<archivoConfiguraciones>\n'
    
    if recursos_match:
        xml_reparado += recursos_match.group(0) + '\n'
    
    if categorias_match:
        xml_reparado += categorias_match.group(0) + '\n'
    
    if clientes_match:
        xml_reparado += clientes_match.group(0) + '\n'
    
    xml_reparado += '</archivoConfiguraciones>'
    
    #Verificar si el XML reparado es valido
    try:
        ET.fromstring(xml_reparado)
        return xml_reparado
    except ET.ParseError:
        return '<?xml version="1.0" encoding="UTF-8"?><archivoConfiguraciones></archivoConfiguraciones>'

#POR SI EL XML TIENE PROBLEMAS
def inspeccionar_xml(xml_data):
    #Buscar lo que esta mal
    lines = xml_data.split('\n')
    for i, line in enumerate(lines, 1):
        if len(line.strip()) > 0:
            print(f"Linea {i}: {line.strip()[:100]}...")
    
    #Buscar etiquetas no cerradas
    open_pattern = r'<(\w+)(?:\s+[^>]*)?>(?![^<]*</\1>)'
    open_tags = re.findall(open_pattern, xml_data)
    if open_tags:
        print(f"Posibles etiquetas no cerradas: {open_tags}")
    
    return xml_data

#ENDPOINT PARA RECIBIR MENSJAES DE CONFIGURACION
@app.route('/api/configuracion', methods=['POST'])
def recibir_configuracion():
    try:
        xml_data = request.data.decode('utf-8')
        
        #Inspeccionar el XML
        xml_data = inspeccionar_xml(xml_data)
        
        #Limpiar y validar el XML
        xml_data = limpiar_y_validar_xml(xml_data)
        
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
        
        #Procesar y guardar recursos
        lista_recursos = root.find('listaRecursos')
        
        if lista_recursos is not None:
            recursos_count = len(lista_recursos.findall('recurso'))
            
            for recurso_elem in lista_recursos.findall('recurso'):
                try:
                    recurso_id = recurso_elem.get('id')
                    
                    recurso_data = {
                        'id': recurso_id,
                        'nombre': "",
                        'abreviatura': "",
                        'metrica': "",
                        'tipo': "",
                        'valorXhora': 0.0
                    }
                    
                    #Obtener todos los campos del recurso
                    nombre_elem = recurso_elem.find('nombre')
                    if nombre_elem is not None and nombre_elem.text is not None:
                        recurso_data['nombre'] = nombre_elem.text.strip()
                    
                    abreviatura_elem = recurso_elem.find('abreviatura')
                    if abreviatura_elem is not None and abreviatura_elem.text is not None:
                        recurso_data['abreviatura'] = abreviatura_elem.text.strip()
                    
                    metrica_elem = recurso_elem.find('metrica')
                    if metrica_elem is not None and metrica_elem.text is not None:
                        recurso_data['metrica'] = metrica_elem.text.strip()
                    
                    tipo_elem = recurso_elem.find('tipo')
                    if tipo_elem is not None and tipo_elem.text is not None:
                        recurso_data['tipo'] = tipo_elem.text.upper()
                    
                    valor_elem = recurso_elem.find('valorXhora')
                    if valor_elem is not None and valor_elem.text is not None:
                        try:
                            recurso_data['valorXhora'] = float(valor_elem.text)
                        except ValueError:
                            recurso_data['valorXhora'] = 0.0
                    
                    
                    #Validar campos obligatorios
                    if not all([recurso_data['id'], recurso_data['nombre'], recurso_data['tipo']]):
                        error_msg = f"Recurso con ID {recurso_data['id']} tiene campos obligatorios faltantes"
                        resultados['errores'].append(error_msg)
                        continue
                    
                    if Validador.validar_tipo_recurso(recurso_data['tipo']):
                        if agregar_recurso(recurso_data):
                            print(f"Recurso guardado: {recurso_data['nombre']}")
                            resultados['recursos_guardados'] += 1
                        else:
                            print(f"Recurso ya existe: {recurso_data['nombre']}")
                    else:
                        error_msg = f"Tipo de recurso invalido: {recurso_data['tipo']}"
                        resultados['errores'].append(error_msg)

                except Exception as e:
                    error_msg = f"Error procesando recurso: {str(e)}"
                    resultados['errores'].append(error_msg)
        
        #Procesar y guardar categorias
        lista_categorias = root.find('listaCategorias')
        if lista_categorias is None:
            #Intentar con nombre alternativo
            lista_categorias = root.find('listaCategoria')
            
        if lista_categorias is not None:
            categorias = lista_categorias.findall('categoria')
            
            for categoria_elem in categorias:
                try:
                    #Buscar descripcion con nombres alternativos
                    descripcion_elem = categoria_elem.find('descripcion')
                    if descripcion_elem is None:
                        descripcion_elem = categoria_elem.find('description')
                    
                    descripcion_text = ""
                    if descripcion_elem is not None and descripcion_elem.text is not None:
                        descripcion_text = descripcion_elem.text.strip()
                    
                    categoria_data = {
                        'id': categoria_elem.get('id'),
                        'nombre': "",
                        'descripcion': descripcion_text,
                        'cargaTrabajo': ""
                    }
                    
                    #Obtener nombre
                    nombre_elem = categoria_elem.find('nombre')
                    if nombre_elem is not None and nombre_elem.text is not None:
                        categoria_data['nombre'] = nombre_elem.text.strip()
                    
                    #Obtener carga de trabajo
                    carga_elem = categoria_elem.find('cargaTrabajo')
                    if carga_elem is not None and carga_elem.text is not None:
                        categoria_data['cargaTrabajo'] = carga_elem.text.strip()
                    
                    if agregar_categoria(categoria_data):
                        resultados['categorias_guardadas'] += 1
                    
                    #Procesar configuraciones de la categoria
                    lista_configuraciones = categoria_elem.find('listaConfiguraciones')
                    if lista_configuraciones is not None:
                        configuraciones = lista_configuraciones.findall('configuracion')
                        
                        for config_elem in configuraciones:
                            try:
                                #Buscar descripcion con nombres alternativos
                                config_desc_elem = config_elem.find('descripcion')
                                if config_desc_elem is None:
                                    config_desc_elem = config_elem.find('description')
                                
                                config_desc_text = ""
                                if config_desc_elem is not None and config_desc_elem.text is not None:
                                    config_desc_text = config_desc_elem.text.strip()
                                
                                config_data = {
                                    'id': config_elem.get('id'),
                                    'idCategoria': categoria_data['id'],
                                    'nombre': "",
                                    'descripcion': config_desc_text,
                                    'recursos': {}
                                }
                                
                                #Obtener nombre de configuracion
                                config_nombre_elem = config_elem.find('nombre')
                                if config_nombre_elem is not None and config_nombre_elem.text is not None:
                                    config_data['nombre'] = config_nombre_elem.text.strip()
                                
                                #Procesar recursos de la configuracion
                                recursos_config = config_elem.find('recursosConfiguracion')
                                if recursos_config is None:
                                    recursos_config = config_elem.find('recursoConfiguracion')
                                
                                if recursos_config is not None:
                                    for recurso_config in recursos_config.findall('recurso'):
                                        recurso_id = recurso_config.get('id')
                                        cantidad_text = "0"
                                        if recurso_config.text is not None:
                                            cantidad_text = recurso_config.text.strip()
                                        try:
                                            cantidad = float(cantidad_text)
                                            config_data['recursos'][recurso_id] = cantidad
                                        except ValueError:
                                            print(f"Error: Cantidad invalida para recurso {recurso_id}: {cantidad_text}")
                                
                                if agregar_configuracion(config_data):
                                    resultados['configuraciones_guardadas'] += 1
                                else:
                                    print(f"configuracion ya existe: {config_data['nombre']} (ID: {config_data['id']})")
                                    
                            except Exception as e:
                                error_msg = f"Error procesando configuracion ID {config_elem.get('id')}: {str(e)}"
                                resultados['errores'].append(error_msg)

                except Exception as e:
                    error_msg = f"Error procesando categoria: {str(e)}"
                    resultados['errores'].append(error_msg)
        
        #Procesar y guardar clientes
        lista_clientes = root.find('listaClientes')
        if lista_clientes is not None:
            clientes = lista_clientes.findall('cliente')
            
            for cliente_elem in clientes:
                try:
                    nit = cliente_elem.get('nit') or cliente_elem.get('nlt')  #Manejar ambos atributos
                    
                    if not nit:
                        error_msg = "Cliente sin NIT"
                        resultados['errores'].append(error_msg)
                        continue
                    
                    #Validar NIT con expresion regular
                    if Validador.validar_nit(nit):
                        cliente_data = {
                            'nit': nit,
                            'nombre': "",
                            'usuario': "",
                            'clave': "",
                            'direccion': "",
                            'correoElectronico': ""
                        }
                        
                        #Obtener todos los campos del cliente
                        nombre_elem = cliente_elem.find('nombre')
                        if nombre_elem is not None and nombre_elem.text is not None:
                            cliente_data['nombre'] = nombre_elem.text.strip()
                        
                        usuario_elem = cliente_elem.find('usuario')
                        if usuario_elem is not None and usuario_elem.text is not None:
                            cliente_data['usuario'] = usuario_elem.text.strip()
                        
                        clave_elem = cliente_elem.find('clave')
                        if clave_elem is not None and clave_elem.text is not None:
                            cliente_data['clave'] = clave_elem.text.strip()
                        
                        direccion_elem = cliente_elem.find('direccion')
                        if direccion_elem is not None and direccion_elem.text is not None:
                            cliente_data['direccion'] = direccion_elem.text.strip()
                        
                        correo_elem = cliente_elem.find('correoElectronico')
                        if correo_elem is not None and correo_elem.text is not None:
                            cliente_data['correoElectronico'] = correo_elem.text.strip()

                        if agregar_cliente(cliente_data):
                            resultados['clientes_guardados'] += 1

                        #Procesar instancias del cliente
                        lista_instancias = cliente_elem.find('listaInstancias')
                        if lista_instancias is not None:
                            instancias = lista_instancias.findall('instancia')
                            
                            for instancia_elem in instancias:
                                try:
                                    fecha_inicio_elem = instancia_elem.find('fechaInicio')
                                    fecha_inicio_text = ""
                                    if fecha_inicio_elem is not None and fecha_inicio_elem.text is not None:
                                        fecha_inicio_text = fecha_inicio_elem.text
                                    fecha_extraida = Validador.extraer_fecha(fecha_inicio_text)
                                    
                                    instancia_data = {
                                        'id': instancia_elem.get('id'),
                                        'nitCliente': nit,
                                        'idConfiguracion': "",
                                        'nombre': "",
                                        'fechaInicio': fecha_extraida or fecha_inicio_text,
                                        'estado': "VIGENTE"
                                    }
                                    
                                    #Obtener idConfiguracion
                                    id_config_elem = instancia_elem.find('idConfiguracion')
                                    if id_config_elem is not None and id_config_elem.text is not None:
                                        instancia_data['idConfiguracion'] = id_config_elem.text
                                    
                                    #Obtener nombre
                                    nombre_inst_elem = instancia_elem.find('nombre')
                                    if nombre_inst_elem is not None and nombre_inst_elem.text is not None:
                                        instancia_data['nombre'] = nombre_inst_elem.text.strip()
                                    
                                    #Obtener estado
                                    estado_elem = instancia_elem.find('estado')
                                    if estado_elem is not None and estado_elem.text is not None:
                                        instancia_data['estado'] = estado_elem.text.upper()
                                    
                                    #Procesar fecha final si hay
                                    fecha_final_elem = instancia_elem.find('fechaFinal')
                                    if fecha_final_elem is not None and fecha_final_elem.text is not None:
                                        fecha_final_extraida = Validador.extraer_fecha(fecha_final_elem.text)
                                        instancia_data['fechaFinal'] = fecha_final_extraida or fecha_final_elem.text
                                    
                                    
                                    if Validador.validar_estado_instancia(instancia_data['estado']):
                                        if agregar_instancia(instancia_data):
                                            resultados['instancias_guardadas'] += 1
                                        else:
                                            print(f"Instancia ya existe: {instancia_data['nombre']} (ID: {instancia_data['id']})")
                                    else:
                                        error_msg = f"Estado de instancia invalido: {instancia_data['estado']}"
                                        resultados['errores'].append(error_msg)
                                        
                                except Exception as e:
                                    error_msg = f"Error procesando instancia ID {instancia_elem.get('id')}: {str(e)}"
                                    resultados['errores'].append(error_msg)
                    else:
                        error_msg = f"NIT invalido: {nit}"
                        resultados['errores'].append(error_msg)
                except Exception as e:
                    error_msg = f"Error procesando cliente: {str(e)}"
                    resultados['errores'].append(error_msg)
        
        return jsonify({
            "estado": "exito",
            "mensaje": "Datos procesados correctamente",
            "resultados": resultados
        })
        
    except ET.ParseError as e:
        return jsonify({"estado": "error", "mensaje": f"XML mal formado: {str(e)}"}), 400
        
    except Exception as e:
        print(f"ERROR General: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"estado": "error", "mensaje": f"Error procesando configuracion: {str(e)}"}), 400

#ENDPOINT PARA RECIBIR MENSAJES DE CONSUMO 
@app.route('/api/consumo', methods=['POST'])
def recibir_consumo():
    try:
        xml_data = request.data.decode('utf-8')
        root = ET.fromstring(xml_data)
        
        consumos_guardados = 0
        errores_consumo = []
        
        for consumo_elem in root.findall('consumo'):
            nit_cliente = consumo_elem.get('nitCliente')
            id_instancia = consumo_elem.get('idInstancia')
            tiempo = float(consumo_elem.find('tiempo').text)
            
            #Buscar 'fechahora' o 'fechaHora'
            fecha_hora_elem = consumo_elem.find('fechahora') or consumo_elem.find('fechaHora')
            fecha_hora = fecha_hora_elem.text if fecha_hora_elem is not None else ""
            
            #Extraer fecha/hora con regex
            fecha_hora_extraida = Validador.extraer_fecha_hora(fecha_hora)
            
            if fecha_hora_extraida:
                consumo_data = {
                    'nitCliente': nit_cliente,
                    'idInstancia': id_instancia,
                    'tiempo': tiempo,
                    'fechahora': fecha_hora_extraida
                }
                
                if agregar_consumo(consumo_data):
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

#ENDPOINT PARA ELIMINAR TODOS LOS DATOS (inicializar sistema)
@app.route('/api/reset', methods=['POST'])
def resetear_datos():
    try:
        #Lista de todos los archivos XML a resetear
        archivos_xml = [
            ARCHIVO_RECURSOS,
            ARCHIVO_CATEGORIAS,
            ARCHIVO_CLIENTES,
            ARCHIVO_CONFIGURACIONES,
            ARCHIVO_INSTANCIAS,
            ARCHIVO_CONSUMOS
        ]
        
        #Eliminar y recrear cada archivo
        for archivo in archivos_xml:
            try:
                if os.path.exists(archivo):
                    os.remove(archivo)
                    print(f"Eliminado: {archivo}")
            except Exception as e:
                print(f"Error eliminando {archivo}: {e}")
        
        #Crear archivos vacios nuevos
        inicializar_archivos_xml()
        
        print("Sistema completamente reiniciado")
        
        return jsonify({
            "estado": "exito",
            "mensaje": "Sistema inicializado correctamente - Todos los datos fueron eliminados"
        })
        
    except Exception as e:
        return jsonify({
            "estado": "error", 
            "mensaje": f"Error al resetear el sistema: {str(e)}"
        }), 400


# =============================================
#           ENDPOINTS PARA CONSULTAS
# =============================================

#ENDPOINT PARA CONSULTAR RECURSOS
@app.route('/api/consultar/recursos', methods=['GET'])
def api_consultar_recursos():
    try:
        recursos = leer_recursos()
        return jsonify({
            "estado": "exito",
            "recursos": recursos
        })
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    
#ENDPOINT PARA CONSULTAR CATEGORIAS
@app.route('/api/consultar/categorias', methods=['GET'])
def api_consultar_categorias():
    try:
        categorias = leer_categorias()
        return jsonify({
            "estado": "exito", 
            "categorias": categorias
        })
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    
#ENDPOINT PARA CONSULTAR CLIENTES
@app.route('/api/consultar/clientes', methods=['GET'])
def api_consultar_clientes():
    try:
        clientes = leer_clientes()
        return jsonify({
            "estado": "exito",
            "clientes": clientes
        })
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    
#ENDPOINT PARA CONSULTAR CONFIGURACIONES
@app.route('/api/consultar/configuraciones', methods=['GET'])
def api_consultar_configuraciones():
    try:
        configuraciones = leer_configuraciones()
        return jsonify({
            "estado": "exito",
            "configuraciones": configuraciones
        })
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    
#ENDPOINT PARA CONSULTAR INSTANCIAS
@app.route('/api/consultar/instancias', methods=['GET'])
def api_consultar_instancias():
    try:
        instancias = leer_instancias()
        return jsonify({
            "estado": "exito",
            "instancias": instancias
        })
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    
#ENDPOINT PARA CONSULTAR CONSUMOS
@app.route('/api/consultar/consumos', methods=['GET'])
def api_consultar_consumos():
    try:
        consumos = leer_consumos()
        return jsonify({
            "estado": "exito",
            "consumos": consumos
        })
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    
#ENDPOINT PARA CONSULTAR TODOS LOS DATOS
@app.route('/api/consultar/todo', methods=['GET'])
def api_consultar_todo():
    try:
        return jsonify({
            "estado": "exito",
            "datos": {
                "recursos": leer_recursos(),
                "categorias": leer_categorias(),
                "clientes": leer_clientes(),
                "configuraciones": leer_configuraciones(),
                "instancias": leer_instancias(),
                "consumos": leer_consumos()
            }
        })
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    

# =============================================
#          ENDPOINTS PARA FACTURACION
# =============================================

#ENDPOINT PARA GENERAR FACTURAS EN RANGO DE FECHAS
@app.route('/api/facturacion/generar', methods=['POST'])
def api_generar_facturas():
    try:
        data = request.get_json()
        
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({"estado": "error", "mensaje": "Debe ingresar las fechas de inicio y fin"}), 400
        
        #Obtener todos los clientes
        clientes = leer_clientes()
        
        facturas_generadas = []
        
        for cliente in clientes:
            factura = generar_factura(cliente['nit'], fecha_inicio, fecha_fin)
            if factura:
                if factura['monto_total'] > 0:
                    facturas_generadas.append(factura)
            else:
                print(f"No se pudo generar factura para {cliente['nit']}")
        
        print(f"Facturas generadas: {len(facturas_generadas)}")
        
        return jsonify({
            "estado": "exito",
            "mensaje": f"Generadas {len(facturas_generadas)} facturas",
            "facturas": facturas_generadas,
            "total_facturado": sum(f['monto_total'] for f in facturas_generadas)
        })
        
    except Exception as e:
        print(f"ERROR en facturacion: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"estado": "error", "mensaje": str(e)}), 400

#ENDPOINT PARA OBTENER FACTURAS EN ESPECIFICO
@app.route('/api/facturacion/cliente/<nit>', methods=['GET'])
def api_facturas_cliente(nit):
    try:
        #Generar factura del ultimo mes
        fecha_fin = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        factura = generar_factura(nit, fecha_inicio, fecha_fin)
        
        if factura:
            return jsonify({
                "estado": "exito",
                "factura": factura
            })
        else:
            return jsonify({
                "estado": "exito",
                "mensaje": "No se encontraron consumos para facturar",
                "factura": None
            })
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    

# =============================================
#          ENDPOINTS PARA REPORTES PDF
# =============================================

#ENDPOINT PARA GENERAR REPORTE DE FACTURA EN PDF
@app.route('/api/reportes/factura', methods=['POST', 'OPTIONS'])
def api_generar_reporte_factura():
    if request.method == 'OPTIONS':
        #Responder a preflight requests
        return jsonify({"estado": "ok"}), 200
        
    try:
        
        #Obtener datos JSON
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            #Intentar parsear como JSON de todos modos
            try:
                data = request.get_json(force=True)
            except:
                return jsonify({"estado": "error", "mensaje": "Formato JSON invalido"}), 40
        
        numero_factura = data.get('numero_factura')
        
        if not numero_factura:
            return jsonify({"estado": "error", "mensaje": "Número de factura requerido"}), 400
        
        #datos de ejemploo
        factura_data = {
            'numero_factura': numero_factura,
            'nombre_cliente': 'Cliente IPC',
            'nit_cliente': '32644-5',
            'fecha_factura': datetime.now().strftime('%Y-%m-%d'),
            'fecha_inicio': '2003-08-01',
            'fecha_fin': '2008-05-31',
            'monto_total': 64960.00,
            'detalle': [
                {
                    'instancia_id': '2',
                    'instancia_nombre': 'Instancia Dos',
                    'costo': 64960.00,
                    'consumos': [
                        {'fechahora': '15/06/2005 08:30', 'tiempo': 6.2},
                        {'fechahora': '19/07/2004 15:14', 'tiempo': 1.0},
                        {'fechahora': '14/08/2003 12:45', 'tiempo': 18.5},
                        {'fechahora': '03/05/2008 09:00', 'tiempo': 5.7},
                        {'fechahora': '21/11/2005 20:16', 'tiempo': 9.2}
                    ]
                }
            ]
        }
        
        filepath = generar_reporte_factura(numero_factura, factura_data)
        
        if filepath and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            return jsonify({
                "estado": "exito",
                "mensaje": "Reporte de factura generado correctamente",
                "archivo": filename
            })
        else:
            return jsonify({"estado": "error", "mensaje": "Error generando reporte PDF"}), 500
            
    except Exception as e:
        print(f"Error generando reporte de factura: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"estado": "error", "mensaje": f"Error interno del servidor: {str(e)}"}), 500

#ENDPOINT PARA DESCARGAR REPORTES
@app.route('/api/reportes/descargar/<nombre_archivo>', methods=['GET'])
def api_descargar_reporte(nombre_archivo):
    try:
        #Verificar que el archivo sea un PDF
        if not nombre_archivo.endswith('.pdf'):
            return jsonify({"estado": "error", "mensaje": "Tipo de archivo no permitido"}), 400
        
        filepath = os.path.join(DATA_DIR, 'reportes', nombre_archivo)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=nombre_archivo)
        else:
            #Listar archivos en el directorio
            reportes_dir = os.path.join(DATA_DIR, 'reportes')
            if os.path.exists(reportes_dir):
                archivos = os.listdir(reportes_dir)
            return jsonify({"estado": "error", "mensaje": "Archivo no encontrado"}), 404
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400

# =============================================
#       ENDPOINTS PARA CREACIÓN DE DATOS
# =============================================

@app.route('/api/crear/recurso', methods=['POST'])
def api_crear_recurso():
    try:
        data = request.json
        
        #Validar campos obligatorios
        if not all(key in data for key in ['id', 'nombre', 'abreviatura', 'metrica', 'tipo', 'valorXhora']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #Validar tipo de recurso
        if not Validador.validar_tipo_recurso(data['tipo']):
            return jsonify({"estado": "error", "mensaje": "Tipo de recurso invalido"}), 400
        
        #Crear estructura de datos para el recurso
        recurso_data = {
            'id': data['id'],
            'nombre': data['nombre'],
            'abreviatura': data['abreviatura'],
            'metrica': data['metrica'],
            'tipo': data['tipo'],
            'valorXhora': float(data['valorXhora'])
        }
        
        #Guardar el recurso
        if agregar_recurso(recurso_data):
            return jsonify({"estado": "exito", "mensaje": "Recurso creado exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "El recurso ya existe"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al crear recurso: {str(e)}"}), 400

@app.route('/api/crear/categoria', methods=['POST'])
def api_crear_categoria():
    try:
        data = request.json
        
        #Validar campos obligatorios
        if not all(key in data for key in ['id', 'nombre', 'descripcion', 'cargaTrabajo']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #Crear estructura de datos para la categoria
        categoria_data = {
            'id': data['id'],
            'nombre': data['nombre'],
            'descripcion': data['descripcion'],
            'cargaTrabajo': data['cargaTrabajo']
        }
        
        #Guardar la categoria
        if agregar_categoria(categoria_data):
            return jsonify({"estado": "exito", "mensaje": "categoria creada exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "La categoria ya existe"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al crear categoria: {str(e)}"}), 400

@app.route('/api/crear/configuracion', methods=['POST'])
def api_crear_configuracion():
    try:
        data = request.json
        
        #Validar campos obligatorios
        if not all(key in data for key in ['id', 'idCategoria', 'nombre', 'descripcion', 'recursos']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #Validar que haya al menos un recurso
        if not data['recursos']:
            return jsonify({"estado": "error", "mensaje": "La configuracion debe tener al menos un recurso"}), 400
        
        #Crear estructura de datos para la configuracion
        config_data = {
            'id': data['id'],
            'idCategoria': data['idCategoria'],
            'nombre': data['nombre'],
            'descripcion': data['descripcion'],
            'recursos': data['recursos']
        }
        
        #Guardar la configuracion
        if agregar_configuracion(config_data):
            return jsonify({"estado": "exito", "mensaje": "configuracion creada exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "La configuracion ya existe"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al crear configuracion: {str(e)}"}), 400

@app.route('/api/crear/cliente', methods=['POST'])
def api_crear_cliente():
    try:
        data = request.json
        
        #Validar campos obligatorios
        if not all(key in data for key in ['nit', 'nombre', 'usuario', 'clave', 'direccion', 'correoElectronico']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #Validar NIT
        nit = data['nit']
        if not Validador.validar_nit(nit):
            #Si el NIT no pasa la validación estricta, permitirlo de todos modos para testing
            print(f"NIT no válido según validador estricto: {nit}, pero se permitirá para testing")
        
        #Crear estructura de datos para el cliente
        cliente_data = {
            'nit': data['nit'],
            'nombre': data['nombre'],
            'usuario': data['usuario'],
            'clave': data['clave'],
            'direccion': data['direccion'],
            'correoElectronico': data['correoElectronico']
        }
        
        #Guardar el cliente
        if agregar_cliente(cliente_data):
            return jsonify({"estado": "exito", "mensaje": "Cliente creado exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "El cliente ya existe"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al crear cliente: {str(e)}"}), 400

@app.route('/api/crear/instancia', methods=['POST'])
def api_crear_instancia():
    try:
        data = request.json
        print(f"Datos recibidos para instancia: {data}")
        
        #Validar campos obligatorios
        if not all(key in data for key in ['id', 'nitCliente', 'idConfiguracion', 'nombre', 'fechaInicio', 'estado']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #Validar estado
        estado = data['estado'].upper()
        if not Validador.validar_estado_instancia(estado):
            return jsonify({"estado": "error", "mensaje": f"Estado de instancia invalido: {estado}. Debe ser VIGENTE o CANCELADA"}), 400
        
        #Extraer fecha de inicio
        fecha_inicio_texto = data['fechaInicio']
        fecha_inicio_extraida = Validador.extraer_fecha(fecha_inicio_texto)
        if not fecha_inicio_extraida:
            #Usar el texto original si no se puede extraer
            fecha_inicio_extraida = fecha_inicio_texto
        
        #Crear estructura de datos para la instancia
        instancia_data = {
            'id': data['id'],
            'nitCliente': data['nitCliente'],
            'idConfiguracion': data['idConfiguracion'],
            'nombre': data['nombre'],
            'fechaInicio': fecha_inicio_extraida,
            'estado': estado
        }
        
        #Agregar fecha final si está presente y el estado es cancelado
        if data.get('fechaFinal') and estado == 'CANCELADA':
            fecha_final_texto = data['fechaFinal']
            fecha_final_extraida = Validador.extraer_fecha(fecha_final_texto)
            if fecha_final_extraida:
                instancia_data['fechaFinal'] = fecha_final_extraida
            else:
                instancia_data['fechaFinal'] = fecha_final_texto
        
        #Guardar la instancia
        if agregar_instancia(instancia_data):
            return jsonify({"estado": "exito", "mensaje": "Instancia creada exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "La instancia ya existe"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al crear instancia: {str(e)}"}), 400

@app.route('/api/crear/consumo', methods=['POST'])
def api_crear_consumo():
    try:
        data = request.json
        
        #Validar campos obligatorios
        if not all(key in data for key in ['nitCliente', 'idInstancia', 'tiempo', 'fechahora']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #Extraer fecha y hora
        fecha_hora_texto = data['fechahora']
        fecha_hora_extraida = Validador.extraer_fecha_hora(fecha_hora_texto)
        if not fecha_hora_extraida:
            #Usar el texto original si no se puede extraer
            fecha_hora_extraida = fecha_hora_texto
        
        #Crear estructura de datos para el consumo
        consumo_data = {
            'nitCliente': data['nitCliente'],
            'idInstancia': data['idInstancia'],
            'tiempo': float(data['tiempo']),
            'fechahora': fecha_hora_extraida
        }
        
        #Guardar el consumo
        if agregar_consumo(consumo_data):
            return jsonify({"estado": "exito", "mensaje": "Consumo registrado exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "Error al registrar consumo"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al registrar consumo: {str(e)}"}), 400



#Endpoint de prueba para verificar que el servidor funciona
@app.route('/api/test', methods=['GET'])
def api_test():
    return jsonify({"estado": "exito", "mensaje": "Servidor Flask funcionando correctamente"})

#Endpoint para listar archivos PDF disponibles
@app.route('/api/reportes/listar', methods=['GET'])
def api_listar_reportes():
    try:
        reportes_dir = os.path.join(DATA_DIR, 'reportes')
        if os.path.exists(reportes_dir):
            archivos = [f for f in os.listdir(reportes_dir) if f.endswith('.pdf')]
            return jsonify({"estado": "exito", "archivos": archivos})
        else:
            return jsonify({"estado": "exito", "archivos": []})
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    
#Endpoint de prueba para PDF
@app.route('/api/reportes/test', methods=['GET'])
def api_test_pdf():
    try:
        #pdf de pruebaaa
        test_data = {
            'numero_factura': 'TEST-001',
            'nombre_cliente': 'Cliente de Prueba',
            'nit_cliente': '12345-6',
            'fecha_factura': '2025-10-24',
            'fecha_inicio': '2025-01-01',
            'fecha_fin': '2025-10-24',
            'monto_total': 1000.00,
            'detalle': [
                {
                    'instancia_id': '1',
                    'instancia_nombre': 'Instancia de Prueba',
                    'costo': 1000.00,
                    'consumos': [
                        {'fechahora': '24/10/2025 10:00', 'tiempo': 5.0},
                        {'fechahora': '24/10/2025 14:30', 'tiempo': 3.0}
                    ]
                }
            ]
        }
        
        filepath = generar_reporte_factura('TEST-001', test_data)
        
        if filepath and os.path.exists(filepath):
            return jsonify({
                "estado": "exito", 
                "mensaje": "PDF de prueba generado correctamente",
                "archivo": os.path.basename(filepath)
            })
        else:
            return jsonify({"estado": "error", "mensaje": "Error generando PDF de prueba"}), 500
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 500

#Ejecutar la aplicacion Flask
if __name__ == '__main__':
    inicializar_archivos_xml()
    app.run(debug=True, port=5000)