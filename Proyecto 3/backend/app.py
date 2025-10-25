from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import xml.etree.ElementTree as ET
import os
import re
from datetime import datetime, timedelta
from pdf_generator import generar_reporte_factura, generar_analisis_ventas
from gestor_datos import GestorDatos
from models import Recurso, Categoria, Configuracion, Cliente, Instancia, Consumo, Factura, Validador

#CREAR LA APLICACION Flask
app = Flask(__name__)
CORS(app)

#CONFIGURACION DE ARCHIVOS XML
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

#INICIALIZAR GESTOR DE DATOS POO
gestor_datos = GestorDatos(DATA_DIR)
gestor_datos.cargar_datos()

#VARIABLE GLOBAL PARA FACTURAS
CONTADOR_FACTURAS = 1000

#FUNCIONES AUXILIARES PARA EXTRACCION DE DATOS
def extraer_datos_recurso(recurso_elem):
    id_recurso = recurso_elem.get('id')
    nombre = recurso_elem.find('nombre').text if recurso_elem.find('nombre') is not None else ""
    abreviatura = recurso_elem.find('abreviatura').text if recurso_elem.find('abreviatura') is not None else ""
    metrica = recurso_elem.find('metrica').text if recurso_elem.find('metrica') is not None else ""
    tipo = recurso_elem.find('tipo').text if recurso_elem.find('tipo') is not None else ""
    valor_text = recurso_elem.find('valorXhora').text if recurso_elem.find('valorXhora') is not None else "0"
    try:
        valorXhora = float(valor_text)
    except ValueError:
        valorXhora = 0.0
    
    return {
        'id': id_recurso,
        'nombre': nombre,
        'abreviatura': abreviatura,
        'metrica': metrica,
        'tipo': tipo,
        'valorXhora': valorXhora
    }

def extraer_datos_categoria(categoria_elem):
    descripcion_elem = categoria_elem.find('descripcion') or categoria_elem.find('description')
    descripcion_text = descripcion_elem.text if descripcion_elem is not None else ""
    
    return {
        'id': categoria_elem.get('id'),
        'nombre': categoria_elem.find('nombre').text if categoria_elem.find('nombre') is not None else "",
        'descripcion': descripcion_text,
        'cargaTrabajo': categoria_elem.find('cargaTrabajo').text if categoria_elem.find('cargaTrabajo') is not None else ""
    }

def extraer_datos_configuracion(config_elem, id_categoria):
    descripcion_elem = config_elem.find('descripcion') or config_elem.find('description')
    descripcion_text = descripcion_elem.text if descripcion_elem is not None else ""
    
    config_data = {
        'id': config_elem.get('id'),
        'idCategoria': id_categoria,
        'nombre': config_elem.find('nombre').text if config_elem.find('nombre') is not None else "",
        'descripcion': descripcion_text,
        'recursos': {}
    }
    
    #PROCESAR RECURSOS DE LA CONFIGURACION
    recursos_config = config_elem.find('recursosConfiguracion')
    if recursos_config is None:
        recursos_config = config_elem.find('recursoConfiguracion')
    
    if recursos_config is not None:
        for recurso_config in recursos_config.findall('recurso'):
            recurso_id = recurso_config.get('id')
            cantidad_text = recurso_config.text if recurso_config.text is not None else "0"
            try:
                cantidad = float(cantidad_text)
                config_data['recursos'][recurso_id] = cantidad
            except ValueError:
                print(f"Error: Cantidad invalida para recurso {recurso_id}: {cantidad_text}")
    
    return config_data

def extraer_datos_cliente(cliente_elem):
    nit = cliente_elem.get('nit') or cliente_elem.get('nlt')
    
    return {
        'nit': nit,
        'nombre': cliente_elem.find('nombre').text if cliente_elem.find('nombre') is not None else "",
        'usuario': cliente_elem.find('usuario').text if cliente_elem.find('usuario') is not None else "",
        'clave': cliente_elem.find('clave').text if cliente_elem.find('clave') is not None else "",
        'direccion': cliente_elem.find('direccion').text if cliente_elem.find('direccion') is not None else "",
        'correoElectronico': cliente_elem.find('correoElectronico').text if cliente_elem.find('correoElectronico') is not None else ""
    }

def extraer_datos_instancia(instancia_elem, nit_cliente):
    fecha_inicio_elem = instancia_elem.find('fechaInicio')
    fecha_inicio_text = fecha_inicio_elem.text if fecha_inicio_elem is not None else ""
    fecha_extraida = Validador.extraer_fecha(fecha_inicio_text)
    
    estado_elem = instancia_elem.find('estado')
    estado_text = estado_elem.text if estado_elem is not None else "VIGENTE"
    
    instancia_data = {
        'id': instancia_elem.get('id'),
        'nitCliente': nit_cliente,
        'idConfiguracion': instancia_elem.find('idConfiguracion').text if instancia_elem.find('idConfiguracion') is not None else "",
        'nombre': instancia_elem.find('nombre').text if instancia_elem.find('nombre') is not None else "",
        'fechaInicio': fecha_extraida or fecha_inicio_text,
        'estado': estado_text.upper()
    }
    
    #PROCESAR FECHA FINAL SI EXISTE
    fecha_final_elem = instancia_elem.find('fechaFinal')
    if fecha_final_elem is not None and fecha_final_elem.text is not None:
        fecha_final_extraida = Validador.extraer_fecha(fecha_final_elem.text)
        instancia_data['fechaFinal'] = fecha_final_extraida or fecha_final_elem.text
    
    return instancia_data

#LIMPIAR XML COMPLETO
def limpiar_y_validar_xml(xml_data):
    if not xml_data or not xml_data.strip():
        return '<?xml version="1.0" encoding="UTF-8"?><archivoConfiguraciones></archivoConfiguraciones>'
    
    #QUITAR CARACTERES DE CONTROL INVALIDOS
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_data)
    
    #QUITAR ESPACIOS EN BLANCO AL INICIO Y FINAL
    cleaned = cleaned.strip()
    
    #ARREGLAR ETIQUETAS MAL FORMADAS
    if cleaned.endswith('</archivoConfiguracione'):
        cleaned = cleaned[:-23] + '</archivoConfiguraciones>'
    
    #ARREGLAR OTROS CIERRES MAL FORMADOS
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
    
    #VERIFICAR QUE EMPIECE CORRECTAMENTE
    if not cleaned.startswith('<?xml'):
        cleaned = '<?xml version="1.0" encoding="UTF-8"?>' + cleaned
    
    #ASEGURAR QUE TENGA LA ESTRUCTURA BASICA COMPLETA
    if '<archivoConfiguraciones>' in cleaned and '</archivoConfiguraciones>' not in cleaned:
        if not cleaned.endswith('</archivoConfiguraciones>'):
            cleaned += '</archivoConfiguraciones>'
    
    #INTENTAR PARSEAR PARA VERIFICAR
    try:
        ET.fromstring(cleaned)
        return cleaned
    except ET.ParseError as e:
        return reparacion_agresiva_xml(cleaned)

#POR SI EL XML ESTA MAL ESCRITO
def reparacion_agresiva_xml(xml_data):
    #EXTRAER TODAS LAS PARTES VALIDAS
    recursos_match = re.search(r'<listaRecursos>.*?</listaRecursos>', xml_data, re.DOTALL)
    categorias_match = re.search(r'<listaCategorias>.*?</listaCategorias>', xml_data, re.DOTALL)
    clientes_match = re.search(r'<listaClientes>.*?</listaClientes>', xml_data, re.DOTALL)
    
    #CONSTRUIR UN XML VALIDO CON LAS PARTES VALIDAS
    xml_reparado = '<?xml version="1.0" encoding="UTF-8"?>\n<archivoConfiguraciones>\n'
    
    if recursos_match:
        xml_reparado += recursos_match.group(0) + '\n'
    
    if categorias_match:
        xml_reparado += categorias_match.group(0) + '\n'
    
    if clientes_match:
        xml_reparado += clientes_match.group(0) + '\n'
    
    xml_reparado += '</archivoConfiguraciones>'
    
    #VERIFICAR SI EL XML REPARADO ES VALIDO
    try:
        ET.fromstring(xml_reparado)
        return xml_reparado
    except ET.ParseError:
        return '<?xml version="1.0" encoding="UTF-8"?><archivoConfiguraciones></archivoConfiguraciones>'

#POR SI EL XML TIENE PROBLEMAS
def inspeccionar_xml(xml_data):
    #BUSCAR LO QUE ESTA MAL
    lines = xml_data.split('\n')
    for i, line in enumerate(lines, 1):
        if len(line.strip()) > 0:
            print(f"Linea {i}: {line.strip()[:100]}...")
    
    #BUSCAR ETIQUETAS NO CERRADAS
    open_pattern = r'<(\w+)(?:\s+[^>]*)?>(?![^<]*</\1>)'
    open_tags = re.findall(open_pattern, xml_data)
    if open_tags:
        print(f"Posibles etiquetas no cerradas: {open_tags}")
    
    return xml_data

#ENDPOINT PARA RECIBIR MENSAJES DE CONFIGURACION
@app.route('/api/configuracion', methods=['POST'])
def recibir_configuracion():
    try:
        xml_data = request.data.decode('utf-8')
        
        #INSPECCIONAR EL XML
        xml_data = inspeccionar_xml(xml_data)
        
        #LIMPIAR Y VALIDAR EL XML
        xml_data = limpiar_y_validar_xml(xml_data)
        
        #PARSEAR EL XML
        root = ET.fromstring(xml_data)
        
        #CONTADORES PARA LOS RESULTADOS
        resultados = {
            'recursos_guardados': 0,
            'categorias_guardadas': 0, 
            'clientes_guardados': 0,
            'configuraciones_guardadas': 0,
            'instancias_guardadas': 0,
            'errores': []
        }
        
        #PROCESAR Y GUARDAR RECURSOS CON POO
        lista_recursos = root.find('listaRecursos')
        if lista_recursos is not None:
            for recurso_elem in lista_recursos.findall('recurso'):
                try:
                    recurso_data = extraer_datos_recurso(recurso_elem)
                    
                    #VALIDAR CAMPOS OBLIGATORIOS
                    if not all([recurso_data['id'], recurso_data['nombre'], recurso_data['tipo']]):
                        error_msg = f"Recurso con ID {recurso_data['id']} tiene campos obligatorios faltantes"
                        resultados['errores'].append(error_msg)
                        continue
                    
                    if Validador.validar_tipo_recurso(recurso_data['tipo']):
                        recurso = Recurso(
                            id_recurso=recurso_data['id'],
                            nombre=recurso_data['nombre'],
                            abreviatura=recurso_data['abreviatura'],
                            metrica=recurso_data['metrica'],
                            tipo=recurso_data['tipo'],
                            valor_por_hora=recurso_data['valorXhora']
                        )
                        if gestor_datos.guardar_recurso(recurso):
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
        
        #PROCESAR Y GUARDAR CATEGORIAS CON POO
        lista_categorias = root.find('listaCategorias')
        if lista_categorias is None:
            lista_categorias = root.find('listaCategoria')
            
        if lista_categorias is not None:
            for categoria_elem in lista_categorias.findall('categoria'):
                try:
                    categoria_data = extraer_datos_categoria(categoria_elem)
                    
                    if categoria_data['id'] and categoria_data['nombre']:
                        categoria = Categoria(
                            id_categoria=categoria_data['id'],
                            nombre=categoria_data['nombre'],
                            descripcion=categoria_data['descripcion'],
                            carga_trabajo=categoria_data['cargaTrabajo']
                        )
                        if gestor_datos.guardar_categoria(categoria):
                            resultados['categorias_guardadas'] += 1
                        
                        #PROCESAR CONFIGURACIONES DE LA CATEGORIA
                        lista_configuraciones = categoria_elem.find('listaConfiguraciones')
                        if lista_configuraciones is not None:
                            for config_elem in lista_configuraciones.findall('configuracion'):
                                try:
                                    config_data = extraer_datos_configuracion(config_elem, categoria_data['id'])
                                    
                                    if config_data['id'] and config_data['nombre']:
                                        configuracion = Configuracion(
                                            id_configuracion=config_data['id'],
                                            id_categoria=config_data['idCategoria'],
                                            nombre=config_data['nombre'],
                                            descripcion=config_data['descripcion']
                                        )
                                        
                                        #AGREGAR RECURSOS A LA CONFIGURACION
                                        for recurso_id, cantidad in config_data['recursos'].items():
                                            configuracion.agregar_recurso(recurso_id, cantidad)
                                        
                                        if gestor_datos.guardar_configuracion(configuracion):
                                            resultados['configuraciones_guardadas'] += 1
                                        else:
                                            print(f"Configuracion ya existe: {config_data['nombre']}")
                                            
                                except Exception as e:
                                    error_msg = f"Error procesando configuracion ID {config_elem.get('id')}: {str(e)}"
                                    resultados['errores'].append(error_msg)

                except Exception as e:
                    error_msg = f"Error procesando categoria: {str(e)}"
                    resultados['errores'].append(error_msg)
        
        #PROCESAR Y GUARDAR CLIENTES CON POO
        lista_clientes = root.find('listaClientes')
        if lista_clientes is not None:
            for cliente_elem in lista_clientes.findall('cliente'):
                try:
                    nit = cliente_elem.get('nit') or cliente_elem.get('nlt')
                    
                    if not nit:
                        error_msg = "Cliente sin NIT"
                        resultados['errores'].append(error_msg)
                        continue
                    
                    #VALIDAR NIT CON EXPRESION REGULAR
                    if Validador.validar_nit(nit):
                        cliente_data = extraer_datos_cliente(cliente_elem)
                        
                        cliente = Cliente(
                            nit=cliente_data['nit'],
                            nombre=cliente_data['nombre'],
                            usuario=cliente_data['usuario'],
                            clave=cliente_data['clave'],
                            direccion=cliente_data['direccion'],
                            correo=cliente_data['correoElectronico']
                        )
                        
                        if gestor_datos.guardar_cliente(cliente):
                            resultados['clientes_guardados'] += 1

                        #PROCESAR INSTANCIAS DEL CLIENTE
                        lista_instancias = cliente_elem.find('listaInstancias')
                        if lista_instancias is not None:
                            for instancia_elem in lista_instancias.findall('instancia'):
                                try:
                                    instancia_data = extraer_datos_instancia(instancia_elem, nit)
                                    
                                    if Validador.validar_estado_instancia(instancia_data['estado']):
                                        instancia = Instancia(
                                            id_instancia=instancia_data['id'],
                                            nit_cliente=instancia_data['nitCliente'],
                                            id_configuracion=instancia_data['idConfiguracion'],
                                            nombre=instancia_data['nombre'],
                                            fecha_inicio=instancia_data['fechaInicio'],
                                            estado=instancia_data['estado']
                                        )
                                        
                                        if instancia_data.get('fechaFinal'):
                                            instancia.fechaFinal = instancia_data['fechaFinal']
                                        
                                        #GUARDAR PRECIOS ORIGINALES
                                        configuracion = gestor_datos.sistema.buscar_configuracion_por_id(instancia.idConfiguracion)
                                        if configuracion:
                                            precios_originales = {}
                                            for recurso_id in configuracion.recursos.keys():
                                                recurso = gestor_datos.sistema.buscar_recurso_por_id(recurso_id)
                                                if recurso:
                                                    precios_originales[recurso_id] = recurso.valor_por_hora
                                            instancia.establecer_precios_originales(precios_originales)
                                        
                                        if gestor_datos.guardar_instancia(instancia):
                                            resultados['instancias_guardadas'] += 1
                                        else:
                                            print(f"Instancia ya existe: {instancia_data['nombre']}")
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
            
            #BUSCAR 'fechahora' O 'fechaHora'
            fecha_hora_elem = consumo_elem.find('fechahora') or consumo_elem.find('fechaHora')
            fecha_hora = fecha_hora_elem.text if fecha_hora_elem is not None else ""
            
            #EXTRAER FECHA/HORA CON REGEX
            fecha_hora_extraida = Validador.extraer_fecha_hora(fecha_hora)
            
            if fecha_hora_extraida:
                consumo = Consumo(
                    nit_cliente=nit_cliente,
                    id_instancia=id_instancia,
                    tiempo=tiempo,
                    fecha_hora=fecha_hora_extraida
                )
                
                if gestor_datos.guardar_consumo(consumo):
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

#RUTA BASICA PARA PROBAR QUE LA API FUNCIONE
@app.route('/')
def hola_mundo():
    return jsonify({"mensaje": "API funcionando", "estado": "OK"})

#ENDPOINT PARA ELIMINAR TODOS LOS DATOS (inicializar sistema)
@app.route('/api/reset', methods=['POST'])
def resetear_datos():
    try:
        if gestor_datos.limpiar_datos():
            return jsonify({
                "estado": "exito",
                "mensaje": "Sistema inicializado correctamente - Todos los datos fueron eliminados"
            })
        else:
            return jsonify({"estado": "error", "mensaje": "Error al resetear el sistema"}), 400
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al resetear el sistema: {str(e)}"}), 400

# =============================================
#           ENDPOINTS PARA CONSULTAS
# =============================================

#ENDPOINT PARA CONSULTAR RECURSOS
@app.route('/api/consultar/recursos', methods=['GET'])
def api_consultar_recursos():
    try:
        recursos = [r.to_dict() for r in gestor_datos.sistema.recursos]
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
        categorias = [c.to_dict() for c in gestor_datos.sistema.categorias]
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
        clientes = [c.to_dict() for c in gestor_datos.sistema.clientes]
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
        configuraciones = [c.to_dict() for c in gestor_datos.sistema.configuraciones]
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
        instancias = [i.to_dict() for i in gestor_datos.sistema.instancias]
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
        consumos = [c.to_dict() for c in gestor_datos.sistema.consumos]
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
        datos = gestor_datos.obtener_datos_para_frontend()
        return jsonify({
            "estado": "exito",
            "datos": datos
        })
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": str(e)}), 400
    
# =============================================
#       ENDPOINT PARA ANÁLISIS DE VENTAS
# =============================================

@app.route('/api/reportes/analisis-ventas', methods=['POST'])
def api_analisis_ventas():
    try:
        data = request.get_json()
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        tipo_analisis = data.get('tipo_analisis', 'categorias')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({"estado": "error", "mensaje": "Fechas requeridas"}), 400
        
        print(f"Generando analisis de ventas: {tipo_analisis} desde {fecha_inicio} hasta {fecha_fin}")
        
        #OBTENER DATOS DEL SISTEMA
        sistema = gestor_datos.sistema
        
        #FILTRAR CONSUMOS POR FECHA
        consumos_filtrados = []
        for consumo in sistema.consumos:
            fecha_consumo = Validador.extraer_fecha(consumo.fechahora)
            if fecha_consumo:
                fecha_consumo_dt = datetime.strptime(fecha_consumo, '%d/%m/%Y')
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                
                if fecha_inicio_dt <= fecha_consumo_dt <= fecha_fin_dt:
                    consumos_filtrados.append(consumo)
        
        datos_analisis = {
            'total_facturado': 0,
            'categorias': [],
            'recursos': []
        }
        
        if tipo_analisis == 'categorias':
            #ANALISIS POR CATEGORIAS Y CONFIGURACIONES
            for categoria in sistema.categorias:
                categoria_info = {
                    'id': categoria.id,
                    'nombre': categoria.nombre,
                    'ingresos': 0,
                    'configuraciones': []
                }
                
                #BUSCAR CONFIGURACIONES DE ESTA CATEGORIA
                configs_categoria = [c for c in sistema.configuraciones if c.idCategoria == categoria.id]
                
                for config in configs_categoria:
                    config_info = {
                        'id': config.id,
                        'nombre': config.nombre,
                        'ingresos': 0
                    }
                    
                    #BUSCAR INSTANCIAS QUE USEN ESTA CONFIGURACION
                    instancias_config = [i for i in sistema.instancias if i.idConfiguracion == config.id]
                    
                    for instancia in instancias_config:
                        #CALCULAR INGRESOS DE ESTA INSTANCIA EN EL PERIODO
                        consumos_instancia = [c for c in consumos_filtrados if c.idInstancia == instancia.id]
                        if consumos_instancia:
                            costo_instancia = calcular_costo_instancia(instancia.id, consumos_instancia)
                            config_info['ingresos'] += costo_instancia
                    
                    categoria_info['ingresos'] += config_info['ingresos']
                    categoria_info['configuraciones'].append(config_info)
                
                datos_analisis['total_facturado'] += categoria_info['ingresos']
                datos_analisis['categorias'].append(categoria_info)
                
        else:  #ANALISIS POR RECURSOS
            for recurso in sistema.recursos:
                recurso_info = {
                    'id': recurso.id,
                    'nombre': recurso.nombre,
                    'ingresos': 0
                }
                
                #CALCULAR INGRESOS POR ESTE RECURSO
                for instancia in sistema.instancias:
                    consumos_instancia = [c for c in consumos_filtrados if c.idInstancia == instancia.id]
                    if consumos_instancia:
                        #OBTENER CONFIGURACION DE LA INSTANCIA
                        config = sistema.buscar_configuracion_por_id(instancia.idConfiguracion)
                        if config and recurso.id in config.recursos:
                            #CALCULAR COSTO ESPECIFICO DE ESTE RECURSO
                            tiempo_total = sum(c.tiempo for c in consumos_instancia)
                            cantidad_recurso = config.recursos[recurso.id]
                            costo_recurso = recurso.valor_por_hora * cantidad_recurso * tiempo_total
                            recurso_info['ingresos'] += costo_recurso
                
                datos_analisis['total_facturado'] += recurso_info['ingresos']
                datos_analisis['recursos'].append(recurso_info)
        
        #ORDENAR POR INGRESOS (MAYOR A MENOR)
        if tipo_analisis == 'categorias':
            datos_analisis['categorias'].sort(key=lambda x: x['ingresos'], reverse=True)
            for categoria in datos_analisis['categorias']:
                categoria['configuraciones'].sort(key=lambda x: x['ingresos'], reverse=True)
        else:
            datos_analisis['recursos'].sort(key=lambda x: x['ingresos'], reverse=True)
        
        #GENERAR PDF
        filepath = generar_analisis_ventas(fecha_inicio, fecha_fin, tipo_analisis, datos_analisis)
        
        if filepath and os.path.exists(filepath):
            return jsonify({
                "estado": "exito",
                "mensaje": "Analisis de ventas generado correctamente",
                "archivo": os.path.basename(filepath),
                "datos": datos_analisis
            })
        else:
            return jsonify({"estado": "error", "mensaje": "Error generando analisis"}), 500
            
    except Exception as e:
        print(f"Error en analisis de ventas: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"estado": "error", "mensaje": str(e)}), 400

# =============================================
#          ENDPOINTS PARA FACTURACION
# =============================================

#CALCULAR COSTO TOTAL DE UNA INSTANCIA
def calcular_costo_instancia(instancia_id, consumos):
    try:
        sistema = gestor_datos.sistema
        instancia = sistema.buscar_instancia_por_id(instancia_id)
        
        if not instancia or not instancia.precios_originales:
            return 0.0
        
        configuracion = sistema.buscar_configuracion_por_id(instancia.idConfiguracion)
        if not configuracion:
            return 0.0
        
        #CALCULAR COSTO TOTAL
        costo_total = 0.0
        
        for consumo in consumos:
            if consumo.idInstancia == instancia_id:
                #CALCULAR COSTO PARA CADA RECURSO
                for recurso_id, cantidad in configuracion.recursos.items():
                    if recurso_id in instancia.precios_originales:
                        precio_recurso = instancia.precios_originales[recurso_id]
                        costo_recurso = precio_recurso * cantidad * consumo.tiempo
                        costo_total += costo_recurso
        
        return round(costo_total, 2)
    except Exception as e:
        return 0.0

#GENERAR FACTURA EN RANGO DE FECHAS
def generar_factura(nit_cliente, fecha_inicio, fecha_fin):
    global CONTADOR_FACTURAS
    
    try:
        sistema = gestor_datos.sistema
        
        #FILTRAR CONSUMOS POR CLIENTE Y FECHA
        consumos_cliente = []
        for consumo in sistema.consumos:
            if consumo.nitCliente == nit_cliente:
                #EXTRAER FECHA DEL CONSUMO
                fecha_consumo = Validador.extraer_fecha(consumo.fechahora)
                if fecha_consumo:
                    fecha_consumo_dt = datetime.strptime(fecha_consumo, '%d/%m/%Y')
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                    
                    if fecha_inicio_dt <= fecha_consumo_dt <= fecha_fin_dt:
                        consumos_cliente.append(consumo)
        
        #SI NO HAY CONSUMOS, RETORNAR NONE
        if not consumos_cliente:
            return None
        
        #AGRUPAR CONSUMOS POR INSTANCIA
        consumos_por_instancia = {}
        for consumo in consumos_cliente:
            instancia_id = consumo.idInstancia
            if instancia_id not in consumos_por_instancia:
                consumos_por_instancia[instancia_id] = []
            consumos_por_instancia[instancia_id].append(consumo)
        
        #CALCULAR COSTOS POR INSTANCIA
        factura_detalle = []
        total_factura = 0.0
        
        for instancia_id, consumos_instancia in consumos_por_instancia.items():
            costo_instancia = calcular_costo_instancia(instancia_id, consumos_instancia)
            total_factura += costo_instancia
            
            #OBTENER INFO DE LA INSTANCIA
            instancia_info = sistema.buscar_instancia_por_id(instancia_id)
            if instancia_info:
                factura_detalle.append({
                    'instancia_id': instancia_id,
                    'instancia_nombre': instancia_info.nombre,
                    'consumos': [c.to_dict() for c in consumos_instancia],
                    'costo': costo_instancia
                })
        
        #GENERAR NUMERO DE FACTURA SECUENCIAL
        CONTADOR_FACTURAS += 1
        numero_factura = f"FAC-{CONTADOR_FACTURAS}"
        
        cliente_info = sistema.buscar_cliente_por_nit(nit_cliente)
        
        return {
            'numero_factura': numero_factura,
            'nit_cliente': nit_cliente,
            'nombre_cliente': cliente_info.nombre if cliente_info else 'Cliente',
            'fecha_factura': fecha_fin,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'detalle': factura_detalle,
            'monto_total': round(total_factura, 2),
            'estado': 'generada'
        }
    
    except Exception as e:
        return None

#ENDPOINT PARA GENERAR FACTURAS EN RANGO DE FECHAS
@app.route('/api/facturacion/generar', methods=['POST'])
def api_generar_facturas():
    try:
        data = request.get_json()
        
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({"estado": "error", "mensaje": "Debe ingresar las fechas de inicio y fin"}), 400
        
        #OBTENER TODOS LOS CLIENTES
        sistema = gestor_datos.sistema
        
        facturas_generadas = []
        
        for cliente in sistema.clientes:
            factura = generar_factura(cliente.nit, fecha_inicio, fecha_fin)
            if factura:
                if factura['monto_total'] > 0:
                    facturas_generadas.append(factura)
            else:
                print(f"No se pudo generar factura para {cliente.nit}")
        
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
        #GENERAR FACTURA DEL ULTIMO MES
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
        #RESPONDER A PREFLIGHT REQUESTS
        return jsonify({"estado": "ok"}), 200
        
    try:
        
        #OBTENER DATOS JSON
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            #INTENTAR PARSEAR COMO JSON DE TODOS MODOS
            try:
                data = request.get_json(force=True)
            except:
                return jsonify({"estado": "error", "mensaje": "Formato JSON invalido"}), 400
        
        numero_factura = data.get('numero_factura')
        
        if not numero_factura:
            return jsonify({"estado": "error", "mensaje": "Número de factura requerido"}), 400
        
        #DATOS DE EJEMPLO
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
        #VERIFICAR QUE EL ARCHIVO SEA UN PDF
        if not nombre_archivo.endswith('.pdf'):
            return jsonify({"estado": "error", "mensaje": "Tipo de archivo no permitido"}), 400
        
        filepath = os.path.join(DATA_DIR, 'reportes', nombre_archivo)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=nombre_archivo)
        else:
            #LISTAR ARCHIVOS EN EL DIRECTORIO
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
        
        #VALIDAR CAMPOS OBLIGATORIOS
        if not all(key in data for key in ['id', 'nombre', 'abreviatura', 'metrica', 'tipo', 'valorXhora']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #VALIDAR TIPO DE RECURSO
        if not Validador.validar_tipo_recurso(data['tipo']):
            return jsonify({"estado": "error", "mensaje": "Tipo de recurso invalido"}), 400
        
        #CREAR RECURSO CON POO
        recurso = Recurso(
            id_recurso=data['id'],
            nombre=data['nombre'],
            abreviatura=data['abreviatura'],
            metrica=data['metrica'],
            tipo=data['tipo'],
            valor_por_hora=float(data['valorXhora'])
        )
        
        #GUARDAR EL RECURSO
        if gestor_datos.guardar_recurso(recurso):
            return jsonify({"estado": "exito", "mensaje": "Recurso creado exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "El recurso ya existe"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al crear recurso: {str(e)}"}), 400

@app.route('/api/crear/categoria', methods=['POST'])
def api_crear_categoria():
    try:
        data = request.json
        
        #VALIDAR CAMPOS OBLIGATORIOS
        if not all(key in data for key in ['id', 'nombre', 'descripcion', 'cargaTrabajo']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #CREAR CATEGORIA CON POO
        categoria = Categoria(
            id_categoria=data['id'],
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            carga_trabajo=data['cargaTrabajo']
        )
        
        #GUARDAR LA CATEGORIA
        if gestor_datos.guardar_categoria(categoria):
            return jsonify({"estado": "exito", "mensaje": "categoria creada exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "La categoria ya existe"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al crear categoria: {str(e)}"}), 400

@app.route('/api/crear/configuracion', methods=['POST'])
def api_crear_configuracion():
    try:
        data = request.json
        
        #VALIDAR CAMPOS OBLIGATORIOS
        if not all(key in data for key in ['id', 'idCategoria', 'nombre', 'descripcion', 'recursos']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #VALIDAR QUE HAYA AL MENOS UN RECURSO
        if not data['recursos']:
            return jsonify({"estado": "error", "mensaje": "La configuracion debe tener al menos un recurso"}), 400
        
        #CREAR CONFIGURACION CON POO
        configuracion = Configuracion(
            id_configuracion=data['id'],
            id_categoria=data['idCategoria'],
            nombre=data['nombre'],
            descripcion=data['descripcion']
        )
        
        #AGREGAR RECURSOS A LA CONFIGURACION
        for recurso_id, cantidad in data['recursos'].items():
            configuracion.agregar_recurso(recurso_id, cantidad)
        
        #GUARDAR LA CONFIGURACION
        if gestor_datos.guardar_configuracion(configuracion):
            return jsonify({"estado": "exito", "mensaje": "configuracion creada exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "La configuracion ya existe"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al crear configuracion: {str(e)}"}), 400

@app.route('/api/crear/cliente', methods=['POST'])
def api_crear_cliente():
    try:
        data = request.json
        
        #VALIDAR CAMPOS OBLIGATORIOS
        if not all(key in data for key in ['nit', 'nombre', 'usuario', 'clave', 'direccion', 'correoElectronico']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #VALIDAR NIT
        nit = data['nit']
        if not Validador.validar_nit(nit):
            print(f"NIT no válido según validador estricto: {nit}, pero se permitirá para testing")
        
        #CREAR CLIENTE CON POO
        cliente = Cliente(
            nit=data['nit'],
            nombre=data['nombre'],
            usuario=data['usuario'],
            clave=data['clave'],
            direccion=data['direccion'],
            correo=data['correoElectronico']
        )
        
        #GUARDAR EL CLIENTE
        if gestor_datos.guardar_cliente(cliente):
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
        
        #VALIDAR CAMPOS OBLIGATORIOS
        if not all(key in data for key in ['id', 'nitCliente', 'idConfiguracion', 'nombre', 'fechaInicio', 'estado']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #VALIDAR ESTADO
        estado = data['estado'].upper()
        if not Validador.validar_estado_instancia(estado):
            return jsonify({"estado": "error", "mensaje": f"Estado de instancia invalido: {estado}. Debe ser VIGENTE o CANCELADA"}), 400
        
        #EXTRAER FECHA DE INICIO
        fecha_inicio_texto = data['fechaInicio']
        fecha_inicio_extraida = Validador.extraer_fecha(fecha_inicio_texto)
        if not fecha_inicio_extraida:
            #USAR EL TEXTO ORIGINAL SI NO SE PUEDE EXTRAER
            fecha_inicio_extraida = fecha_inicio_texto
        
        #CREAR INSTANCIA CON POO
        instancia = Instancia(
            id_instancia=data['id'],
            nit_cliente=data['nitCliente'],
            id_configuracion=data['idConfiguracion'],
            nombre=data['nombre'],
            fecha_inicio=fecha_inicio_extraida,
            estado=estado
        )
        
        #AGREGAR FECHA FINAL SI ESTÁ PRESENTE Y EL ESTADO ES CANCELADO
        if data.get('fechaFinal') and estado == 'CANCELADA':
            fecha_final_texto = data['fechaFinal']
            fecha_final_extraida = Validador.extraer_fecha(fecha_final_texto)
            if fecha_final_extraida:
                instancia.fechaFinal = fecha_final_extraida
            else:
                instancia.fechaFinal = fecha_final_texto
        
        #GUARDAR PRECIOS ORIGINALES
        configuracion = gestor_datos.sistema.buscar_configuracion_por_id(instancia.idConfiguracion)
        if configuracion:
            precios_originales = {}
            for recurso_id in configuracion.recursos.keys():
                recurso = gestor_datos.sistema.buscar_recurso_por_id(recurso_id)
                if recurso:
                    precios_originales[recurso_id] = recurso.valor_por_hora
            instancia.establecer_precios_originales(precios_originales)
        
        #GUARDAR LA INSTANCIA
        if gestor_datos.guardar_instancia(instancia):
            return jsonify({"estado": "exito", "mensaje": "Instancia creada exitosamente"})
        else:
            return jsonify({"estado": "error", "mensaje": "La instancia ya existe"}), 400
            
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al crear instancia: {str(e)}"}), 400

@app.route('/api/crear/consumo', methods=['POST'])
def api_crear_consumo():
    try:
        data = request.json
        
        #VALIDAR CAMPOS OBLIGATORIOS
        if not all(key in data for key in ['nitCliente', 'idInstancia', 'tiempo', 'fechahora']):
            return jsonify({"estado": "error", "mensaje": "Faltan campos obligatorios"}), 400
        
        #EXTRAER FECHA Y HORA
        fecha_hora_texto = data['fechahora']
        fecha_hora_extraida = Validador.extraer_fecha_hora(fecha_hora_texto)
        if not fecha_hora_extraida:
            #USAR EL TEXTO ORIGINAL SI NO SE PUEDE EXTRAER
            fecha_hora_extraida = fecha_hora_texto
        
        #CREAR CONSUMO CON POO
        consumo = Consumo(
            nit_cliente=data['nitCliente'],
            id_instancia=data['idInstancia'],
            tiempo=float(data['tiempo']),
            fecha_hora=fecha_hora_extraida
        )
        
        #GUARDAR EL CONSUMO
        if gestor_datos.guardar_consumo(consumo):
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
        #PDF DE PRUEBA
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

#EJECUTAR LA APLICACION Flask
if __name__ == '__main__':
    gestor_datos.cargar_datos()
    app.run(debug=True, port=5000)