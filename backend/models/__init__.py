import xml.etree.ElementTree as ET
import re
from datetime import datetime

#CLASE PARA RECURSO DE LA NUBE
class Recurso:
    def __init__(self, id_recurso, nombre, abreviatura, metrica, tipo, valor_por_hora):
        self.id = id_recurso
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.metrica = metrica
        self.tipo = tipo #Hardware o Software
        self.valor_por_hora = float(valor_por_hora)

    #CONVERTIR OBJETO A XML PARA GUARDAR EN LA BASE DE DATOS
    def to_xml_element(self):
        recurso_elem = ET.Element('recurso')
        recurso_elem.set('id', str(self.id))

        ET.SubElement(recurso_elem, 'nombre').text = self.nombre
        ET.SubElement(recurso_elem, 'abreviatura').text = self.abreviatura
        ET.SubElement(recurso_elem, 'metrica').text = self.metrica
        ET.SubElement(recurso_elem, 'tipo').text = self.tipo
        ET.SubElement(recurso_elem, 'valorXhora').text = str(self.valor_por_hora)

        return recurso_elem
    
    @classmethod
    #CREAR OBJETO RECURSO DESDE UN ELEMENTO XML
    def from_xml_element(cls, element):
        return cls(
            id_recurso=element.get('id'),
            nombre=element.find('nombre').text,
            abreviatura=element.find('abreviatura').text,
            metrica=element.find('metrica').text,
            tipo=element.find('tipo').text,
            valor_por_hora=element.find('valorXhora').text
        )
    

#CLASE PARA UNA CATEGORIA DE CONFIGURACIONES
class Categoria:
    def __init__(self, id_categoria, nombre, descripcion, carga_trabajo):
        self.id = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self. carga_trabajo = carga_trabajo
        self.configuraciones = []

    def agregar_configuracion(self, configuracion):
        self.configuraciones.append(configuracion)

#CLASE PARA UNA CONFIGURACION ESPECIFICA DE UNA CATEGORIA
class Configuracion:
    def __init__(self, id_configuracion, nombre, descripcion):
        self.id = id_configuracion
        self.nombre = nombre
        self.descripcion = descripcion
        self.recursos = {} #Diccionario {id_recurso: cantidad}

    def agregar_recurso(self, id_recurso, cantidad):
        self.recursos[id_recurso] = float(cantidad)

#CLASE PARA CLIENTE DE LA EMPRESA
class Cliente:
    def __init__(self, nit, nombre, usuario, clave, direccion, correo):
        self.nit = nit
        self.nombre = nombre
        self.usuario = usuario
        self.clave = clave
        self.direccion = direccion
        self.correo = correo
        self.instancias = []

    def agregar_instancia(self, instancia):
        self.instancias.append(instancia)

#CLASE PARA INSTANCIA APROVISIONADA POR UN CLIENTE
class Instancia:
    def __init__(self, id_instancia, id_configuracion, nombre, fecha_inicio, estado="Vigente"):
        self.id = id_instancia
        self.id_configuracion = id_configuracion
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.estado = estado #Vigente o Cancelado
        self.fecha_final = None
        self.consumos = []

    def cancelar(self, fecha_final):
        self.estado = "Cancelada"
        self.fecha_final = fecha_final

#CLASE DEL CONSUMO DE UNA INSTANCIA
class Consumo:
    def __init__(self, id_instancia, tiempo, fecha_hora):
        self.id_instancia = id_instancia
        self.tiempo = float(tiempo)  #Horas de consumo
        self.fecha_hora = fecha_hora

#CLASE DE FACTURA GENERADA
class Factura:
    def __init__(self, numero_factura, nit_cliente, fecha_factura, monto_total):
        self.numero = numero_factura
        self.nit_cliente = nit_cliente
        self.fecha = fecha_factura
        self.monto_total = float(monto_total)
        self.detalles = []  #Detalles de lo que se factura

#CLASE PARA MANEJAR EXPRESIONES REGULARES
class Validador:

    @staticmethod
    #VALIDAR QUE EL NIT TENGA EL FORMATO CORRECTO CON ER
    def validar_nit(nit):
        patron = r'^\d+-[0-9K]$'
        return re.match(patron, nit) is not None
    
    @staticmethod
    #EXTRAER UNA FECHA DEL FORMATO dd/mm/yyyy
    def extraer_fecha(texto):
        patron = r'\b(\d{2}/\d{2}/\d{4})\b'
        coincidencias = re.findall(patron, texto)
        return coincidencias[0] if coincidencias else None
    
    @staticmethod
    #EXTRAER FECHA Y HORA DEL FORMATO dd/mm/yyyy hh24:mi
    def extraer_fecha_hora(texto):
        patron = r'\b(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\b'
        coincidencias = re.findall(patron, texto)
        return coincidencias[0] if coincidencias else None