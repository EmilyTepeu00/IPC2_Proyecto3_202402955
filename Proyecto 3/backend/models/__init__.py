import xml.etree.ElementTree as ET
import re
from datetime import datetime


# CLASE BASE PARA MANEJO XML
class EntidadXML:
    def to_xml_element(self):
        raise NotImplementedError("Método to_xml_element debe ser implementado")
    
    @classmethod
    def from_xml_element(cls, element):
        raise NotImplementedError("Método from_xml_element debe ser implementado")
    
    def to_dict(self):
        return self.__dict__
    
#CLASE PARA RECURSO DE LA NUBE
class Recurso(EntidadXML):
    def __init__(self, id_recurso, nombre, abreviatura, metrica, tipo, valor_por_hora):
        self.id = id_recurso
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.metrica = metrica
        self.tipo = tipo.upper()  #Hardware o Software
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
class Categoria(EntidadXML):
    def __init__(self, id_categoria, nombre, descripcion, carga_trabajo):
        self.id = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.carga_trabajo = carga_trabajo
        self.configuraciones = []

    def agregar_configuracion(self, configuracion):
        self.configuraciones.append(configuracion)

    def to_xml_element(self):
        categoria_elem = ET.Element('categoria')
        categoria_elem.set('id', str(self.id))
        
        ET.SubElement(categoria_elem, 'nombre').text = self.nombre
        ET.SubElement(categoria_elem, 'description').text = self.descripcion
        ET.SubElement(categoria_elem, 'cargaTrabajo').text = self.carga_trabajo
        
        lista_configs = ET.SubElement(categoria_elem, 'listaConfiguraciones')
        for config in self.configuraciones:
            lista_configs.append(config.to_xml_element())
            
        return categoria_elem

    @classmethod
    def from_xml_element(cls, element):
        categoria = cls(
            id_categoria=element.get('id'),
            nombre=element.find('nombre').text,
            descripcion=element.find('description').text,
            carga_trabajo=element.find('cargaTrabajo').text
        )
        
        #Procesar configuraciones si existen
        lista_configs = element.find('listaConfiguraciones')
        if lista_configs is not None:
            for config_elem in lista_configs.findall('configuracion'):
                config = Configuracion.from_xml_element(config_elem)
                categoria.agregar_configuracion(config)
                
        return categoria

#CLASE PARA UNA CONFIGURACION ESPECIFICA DE UNA CATEGORIA
class Configuracion(EntidadXML):
    def __init__(self, id_configuracion, id_categoria, nombre, descripcion):
        self.id = id_configuracion
        self.idCategoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.recursos = {}  

    def agregar_recurso(self, id_recurso, cantidad):
        self.recursos[id_recurso] = float(cantidad)

    def to_xml_element(self):
        config_elem = ET.Element('configuracion')
        config_elem.set('id', str(self.id))
        config_elem.set('idCategoria', str(self.idCategoria))
        
        ET.SubElement(config_elem, 'nombre').text = self.nombre
        ET.SubElement(config_elem, 'description').text = self.descripcion
        
        recursos_config = ET.SubElement(config_elem, 'recursosConfiguracion')
        for recurso_id, cantidad in self.recursos.items():
            recurso_elem = ET.SubElement(recursos_config, 'recurso')
            recurso_elem.set('id', str(recurso_id))
            recurso_elem.text = str(cantidad)
            
        return config_elem

    @classmethod
    def from_xml_element(cls, element):
        config = cls(
            id_configuracion=element.get('id'),
            id_categoria=element.get('idCategoria'),
            nombre=element.find('nombre').text,
            descripcion=element.find('description').text
        )
        
        #Procesar recursos
        recursos_config = element.find('recursosConfiguracion')
        if recursos_config is not None:
            for recurso_elem in recursos_config.findall('recurso'):
                recurso_id = recurso_elem.get('id')
                cantidad = float(recurso_elem.text)
                config.agregar_recurso(recurso_id, cantidad)
                
        return config

#CLASE PARA CLIENTE DE LA EMPRESA
class Cliente(EntidadXML):
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

    def to_xml_element(self):
        cliente_elem = ET.Element('cliente')
        cliente_elem.set('nit', self.nit)
        
        ET.SubElement(cliente_elem, 'nombre').text = self.nombre
        ET.SubElement(cliente_elem, 'usuario').text = self.usuario
        ET.SubElement(cliente_elem, 'clave').text = self.clave
        ET.SubElement(cliente_elem, 'direccion').text = self.direccion
        ET.SubElement(cliente_elem, 'correoElectronico').text = self.correo
        
        lista_instancias = ET.SubElement(cliente_elem, 'listaInstancias')
        for instancia in self.instancias:
            lista_instancias.append(instancia.to_xml_element())
            
        return cliente_elem

    @classmethod
    def from_xml_element(cls, element):
        cliente = cls(
            nit=element.get('nit'),
            nombre=element.find('nombre').text,
            usuario=element.find('usuario').text,
            clave=element.find('clave').text,
            direccion=element.find('direccion').text,
            correo=element.find('correoElectronico').text
        )
        
        #Procesar instancias
        lista_instancias = element.find('listaInstancias')
        if lista_instancias is not None:
            for instancia_elem in lista_instancias.findall('instancia'):
                instancia = Instancia.from_xml_element(instancia_elem)
                cliente.agregar_instancia(instancia)
                
        return cliente

#CLASE PARA INSTANCIA APROVISIONADA POR UN CLIENTE
class Instancia(EntidadXML):
    def __init__(self, id_instancia, nit_cliente, id_configuracion, nombre, fecha_inicio, estado="VIGENTE"):
        self.id = id_instancia
        self.nitCliente = nit_cliente
        self.idConfiguracion = id_configuracion
        self.nombre = nombre
        self.fechaInicio = fecha_inicio
        self.estado = estado.upper()  #VIGENTE o CANCELADA
        self.fechaFinal = None
        self.precios_originales = {}

    def cancelar(self, fecha_final):
        self.estado = "CANCELADA"
        self.fechaFinal = fecha_final

    def establecer_precios_originales(self, precios):
        self.precios_originales = precios

    def to_xml_element(self):
        instancia_elem = ET.Element('instancia')
        instancia_elem.set('id', str(self.id))
        instancia_elem.set('nitCliente', self.nitCliente)
        
        ET.SubElement(instancia_elem, 'idConfiguracion').text = str(self.idConfiguracion)
        ET.SubElement(instancia_elem, 'nombre').text = self.nombre
        ET.SubElement(instancia_elem, 'fechaInicio').text = self.fechaInicio
        ET.SubElement(instancia_elem, 'estado').text = self.estado
        
        if self.fechaFinal:
            ET.SubElement(instancia_elem, 'fechaFinal').text = self.fechaFinal
            
        #Guardar precios originales
        if self.precios_originales:
            precios_elem = ET.SubElement(instancia_elem, 'preciosOriginales')
            for recurso_id, precio in self.precios_originales.items():
                recurso_precio = ET.SubElement(precios_elem, 'recurso')
                recurso_precio.set('id', str(recurso_id))
                recurso_precio.set('precio', str(precio))
            
        return instancia_elem

    @classmethod
    def from_xml_element(cls, element):
        instancia = cls(
            id_instancia=element.get('id'),
            nit_cliente=element.get('nitCliente'),
            id_configuracion=element.find('idConfiguracion').text,
            nombre=element.find('nombre').text,
            fecha_inicio=element.find('fechaInicio').text,
            estado=element.find('estado').text
        )
        
        fecha_final_elem = element.find('fechaFinal')
        if fecha_final_elem is not None:
            instancia.fechaFinal = fecha_final_elem.text
            
        #Cargar precios originales si existen
        precios_elem = element.find('preciosOriginales')
        if precios_elem is not None:
            precios = {}
            for recurso_precio in precios_elem.findall('recurso'):
                precios[recurso_precio.get('id')] = float(recurso_precio.get('precio'))
            instancia.precios_originales = precios
            
        return instancia

#CLASE DEL CONSUMO DE UNA INSTANCIA
class Consumo(EntidadXML):
    def __init__(self, nit_cliente, id_instancia, tiempo, fecha_hora):
        self.nitCliente = nit_cliente
        self.idInstancia = id_instancia
        self.tiempo = float(tiempo)  #Horas de consumo
        self.fechahora = fecha_hora

    def to_xml_element(self):
        consumo_elem = ET.Element('consumo')
        consumo_elem.set('nitCliente', self.nitCliente)
        consumo_elem.set('idInstancia', self.idInstancia)
        
        ET.SubElement(consumo_elem, 'tiempo').text = str(self.tiempo)
        ET.SubElement(consumo_elem, 'fechahora').text = self.fechahora
            
        return consumo_elem

    @classmethod
    def from_xml_element(cls, element):
        return cls(
            nit_cliente=element.get('nitCliente'),
            id_instancia=element.get('idInstancia'),
            tiempo=element.find('tiempo').text,
            fecha_hora=element.find('fechahora').text
        )


#CLASE DE FACTURA GENERADA
class Factura:
    def __init__(self, numero_factura, nit_cliente, fecha_factura, monto_total):
        self.numero_factura = numero_factura
        self.nit_cliente = nit_cliente
        self.fecha_factura = fecha_factura
        self.monto_total = float(monto_total)
        self.detalle = []  #Lista de detalles de instancias facturadas

    def agregar_detalle(self, detalle_instancia):
        self.detalle.append(detalle_instancia)

    def to_dict(self):
        return {
            'numero_factura': self.numero_factura,
            'nit_cliente': self.nit_cliente,
            'fecha_factura': self.fecha_factura,
            'monto_total': self.monto_total,
            'detalle': self.detalle
        }
    
#CLASE PARA MANEJO DE DATOS DEL SISTEMA
class SistemaCloud:
    def __init__(self):
        self.recursos = []
        self.categorias = []
        self.clientes = []
        self.configuraciones = []
        self.instancias = []
        self.consumos = []
        self.facturas = []

    def agregar_recurso(self, recurso):
        self.recursos.append(recurso)

    def agregar_categoria(self, categoria):
        self.categorias.append(categoria)

    def agregar_cliente(self, cliente):
        self.clientes.append(cliente)

    def agregar_configuracion(self, configuracion):
        self.configuraciones.append(configuracion)

    def agregar_instancia(self, instancia):
        self.instancias.append(instancia)

    def agregar_consumo(self, consumo):
        self.consumos.append(consumo)

    def buscar_recurso_por_id(self, id_recurso):
        for recurso in self.recursos:
            if recurso.id == id_recurso:
                return recurso
        return None

    def buscar_configuracion_por_id(self, id_config):
        for config in self.configuraciones:
            if config.id == id_config:
                return config
        return None

    def buscar_cliente_por_nit(self, nit):
        for cliente in self.clientes:
            if cliente.nit == nit:
                return cliente
        return None

    def buscar_instancia_por_id(self, id_instancia):
        for instancia in self.instancias:
            if instancia.id == id_instancia:
                return instancia
        return None

#CLASE PARA MANEJAR EXPRESIONES REGULARES
class Validador:

    @staticmethod
    #VALIDAR QUE EL NIT TENGA EL FORMATO CORRECTO CON ER
    def validar_nit(nit):
        if not nit:
            return False
        patron = r'^\d+[-]?[\dKk]?$'
        return re.match(patron, nit) is not None
    
    @staticmethod
    #EXTRAER UNA FECHA DEL FORMATO dd/mm/yyyy
    def extraer_fecha(texto):
        if not texto:
            return None
        patron = r'\b(\d{1,2}/\d{1,2}/\d{4})\b'
        coincidencias = re.findall(patron, texto)
        return coincidencias[0] if coincidencias else None
    
    @staticmethod
    #EXTRAER FECHA Y HORA DEL FORMATO dd/mm/yyyy hh24:mi
    def extraer_fecha_hora(texto):
        if not texto:
            return None
        patron = r'\b(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2})\b'
        coincidencias = re.findall(patron, texto)
        return coincidencias[0] if coincidencias else None
    
    @staticmethod
    #VALIDAR ESTADO DE INSTANCIA
    def validar_estado_instancia(estado):
        estado_upper = estado.upper()
        return estado_upper in ["VIGENTE", "CANCELADA", "ACTIVA", "CANCELADO"]
    
    @staticmethod
    #VALIDAR TIPO DE RECURSO
    def validar_tipo_recurso(tipo):
        tipo_upper = tipo.upper()
        return tipo_upper in ["HARDWARE", "SOFTWARE", "HW", "SW"]