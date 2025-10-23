from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
import os
import re
from datetime import datetime, timedelta

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

#---- FUNCIONES DE GUARDADO EN EL ARCHIVO XML ----

#AGREGAR UN RECURSO
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

        #Agregar lista de instancias vacia
        lista_instancias = ET.SubElement(cliente_elem, 'listaInstancias')

        lista_instancias = ET.SubElement(cliente_elem, 'listaInstancias')
        
        root.append(cliente_elem)
        tree.write(ARCHIVO_CLIENTES, encoding='utf-8', xml_declaration=True)
        return True
    
    except Exception as e:
        print(f"Error guardando cliente: {e}")
        return False
 
#AGREGAR UNA CONFIGURACION
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
    
#AGREGAR UNA INSTANCIA
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
        print(f"Error guardando instancia: {e}")
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
        print(f"Error guardando consumo: {e}")
        return False

#---- FUNCIONES PARA LEER EL ARCHIVO XML ----

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
    

#---- FUNCIONES PARA FACTURACION ----

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
        print(f"Error guardando precios de instancia: {e}")
        return False
    
#OBTENER LOS PRECIOS ORIGINALES D EUNA INSTANCIA
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
        
        #Obtener CONFIGURACION de la instancia para saber que recursos usa
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
                #Para cada recurso en la configuracion se calcula el costo
                for recurso_id, cantidad in configuracion['recursos'].items():
                    if recurso_id in precios_originales:
                        precio_recurso = precios_originales[recurso_id]
                        costo_recurso = precio_recurso * cantidad * consumo['tiempo']
                        costo_total += costo_recurso
        
        return round(costo_total, 2)
    except Exception as e:
        print(f"Error calculando costo: {e}")
        return 0.0
    
#GENERAR FACTURA EN RANGO DE FECHAS
def generar_factura(nit_cliente, fecha_inicio, fecha_fin):
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
        
        #Generar numero de factura unico
        numero_factura = f"FAC-{datetime.now().strftime('%Y%m%d')}-{nit_cliente}"
        
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
        print(f"Error generando factura: {e}")
        return None


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

#RENDPOINT PARA ELIMINAR TODOS LOS DATOS (inicializar sistema)
@app.route('/api/reset', methods=['POST'])
def resetear_datos():
    try:
        inicializar_archivos_xml()
        return jsonify({"estado": "exito", "mensaje": "Sistema inicializado"})
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error: {str(e)}"}), 400


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
            if factura and factura['monto_total'] > 0:
                facturas_generadas.append(factura)
        
        return jsonify({
            "estado": "exito",
            "mensaje": f"Generadas {len(facturas_generadas)} facturas",
            "facturas": facturas_generadas,
            "total_facturado": sum(f['monto_total'] for f in facturas_generadas)
        })
        
    except Exception as e:
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

#Ejecutar la aplicacion Flask
if __name__ == '__main__':
    inicializar_archivos_xml()
    app.run(debug=True, port=5000)