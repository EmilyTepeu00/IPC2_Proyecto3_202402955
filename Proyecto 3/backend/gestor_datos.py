import os
import xml.etree.ElementTree as ET
from models import Recurso, Categoria, Configuracion, Cliente, Instancia, Consumo, SistemaCloud, Validador

class GestorDatos:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.sistema = SistemaCloud()
        self.archivos = {
            'recursos': os.path.join(data_dir, 'recursos.xml'),
            'categorias': os.path.join(data_dir, 'categorias.xml'),
            'clientes': os.path.join(data_dir, 'clientes.xml'),
            'configuraciones': os.path.join(data_dir, 'configuraciones.xml'),
            'instancias': os.path.join(data_dir, 'instancias.xml'),
            'consumos': os.path.join(data_dir, 'consumos.xml')
        }
        self.inicializar_archivos()

    #CREAR ARCHIVOS XML SI NO HAY
    def inicializar_archivos(self):
        for archivo, tag_raiz in [
            (self.archivos['recursos'], 'recursos'),
            (self.archivos['categorias'], 'categorias'),
            (self.archivos['clientes'], 'clientes'),
            (self.archivos['configuraciones'], 'configuraciones'),
            (self.archivos['instancias'], 'instancias'),
            (self.archivos['consumos'], 'consumos')
        ]:
            if not os.path.exists(archivo):
                root = ET.Element(tag_raiz)
                tree = ET.ElementTree(root)
                with open(archivo, 'w', encoding='utf-8') as f:
                    tree.write(f, encoding='unicode', xml_declaration=True)

    #CARGAR TODOS LOS DATOS DESDE LOS XML
    def cargar_datos(self):
        self.cargar_recursos()
        self.cargar_categorias()
        self.cargar_configuraciones()
        self.cargar_clientes()
        self.cargar_instancias()
        self.cargar_consumos()

    #CARGAR RECURSOS DESDE XML
    def cargar_recursos(self):
        try:
            tree = ET.parse(self.archivos['recursos'])
            root = tree.getroot()
            for recurso_elem in root.findall('recurso'):
                recurso = Recurso.from_xml_element(recurso_elem)
                self.sistema.agregar_recurso(recurso)
        except Exception as e:
            print(f"Error cargando recursos: {e}")

    #CARGAR CATEGORIAS DESDE XML
    def cargar_categorias(self):
        try:
            tree = ET.parse(self.archivos['categorias'])
            root = tree.getroot()
            for categoria_elem in root.findall('categoria'):
                categoria = Categoria.from_xml_element(categoria_elem)
                self.sistema.agregar_categoria(categoria)
        except Exception as e:
            print(f"Error cargando categorías: {e}")

    #CARGAR CONFIGURACIONES DESDE XML
    def cargar_configuraciones(self):
        try:
            tree = ET.parse(self.archivos['configuraciones'])
            root = tree.getroot()
            for config_elem in root.findall('configuracion'):
                config = Configuracion.from_xml_element(config_elem)
                self.sistema.agregar_configuracion(config)
        except Exception as e:
            print(f"Error cargando configuraciones: {e}")

    #CARGAR CLIENTES DESDE XML
    def cargar_clientes(self):
        try:
            tree = ET.parse(self.archivos['clientes'])
            root = tree.getroot()
            for cliente_elem in root.findall('cliente'):
                cliente = Cliente.from_xml_element(cliente_elem)
                self.sistema.agregar_cliente(cliente)
        except Exception as e:
            print(f"Error cargando clientes: {e}")

    #CARGAR INSTANCIAS
    def cargar_instancias(self):
        try:
            tree = ET.parse(self.archivos['instancias'])
            root = tree.getroot()
            for instancia_elem in root.findall('instancia'):
                instancia = Instancia.from_xml_element(instancia_elem)
                self.sistema.agregar_instancia(instancia)
        except Exception as e:
            print(f"Error cargando instancias: {e}")

    #CARGAR CONSUMOS
    def cargar_consumos(self):
        try:
            tree = ET.parse(self.archivos['consumos'])
            root = tree.getroot()
            for consumo_elem in root.findall('consumo'):
                consumo = Consumo.from_xml_element(consumo_elem)
                self.sistema.agregar_consumo(consumo)
        except Exception as e:
            print(f"Error cargando consumos: {e}")

    #GUARDAR UN RECURSO EN XML
    def guardar_recurso(self, recurso):
        if any(r.id == recurso.id for r in self.sistema.recursos):
            return False  # Ya existe
        
        self.sistema.agregar_recurso(recurso)
        return self._guardar_lista('recursos', self.sistema.recursos)

    #GUARDAR UNA CATEGORIA
    def guardar_categoria(self, categoria):
        if any(c.id == categoria.id for c in self.sistema.categorias):
            return False  # Ya existe
        
        self.sistema.agregar_categoria(categoria)
        return self._guardar_lista('categorias', self.sistema.categorias)

    #GUARDAR UNA CONFIGURACION
    def guardar_configuracion(self, configuracion):
        if any(c.id == configuracion.id for c in self.sistema.configuraciones):
            return False  # Ya existe
        
        self.sistema.agregar_configuracion(configuracion)
        return self._guardar_lista('configuraciones', self.sistema.configuraciones)

    #GUARDAR UN CLIENTE
    def guardar_cliente(self, cliente):
        if any(c.nit == cliente.nit for c in self.sistema.clientes):
            return False  # Ya existe
        
        self.sistema.agregar_cliente(cliente)
        return self._guardar_lista('clientes', self.sistema.clientes)

    #GUARDAR UNA INSTANCIA
    def guardar_instancia(self, instancia):
        if any(i.id == instancia.id for i in self.sistema.instancias):
            return False  # Ya existe
        
        self.sistema.agregar_instancia(instancia)
        return self._guardar_lista('instancias', self.sistema.instancias)

    #GUARDAR UN CONSUMO
    def guardar_consumo(self, consumo):
        self.sistema.agregar_consumo(consumo)
        return self._guardar_lista('consumos', self.sistema.consumos)

    #GUARDAR LISTA DE OBJETOS
    def _guardar_lista(self, tipo, lista_objetos):
        try:
            archivo = self.archivos[tipo]
            root = ET.Element(tipo)  #El nombre del elemento raiz es el tipo
            
            for obj in lista_objetos:
                root.append(obj.to_xml_element())
            
            tree = ET.ElementTree(root)
            with open(archivo, 'w', encoding='utf-8') as f:
                tree.write(f, encoding='unicode', xml_declaration=True)
            return True
        except Exception as e:
            print(f"Error guardando {tipo}: {e}")
            return False

    #CONVERTIR DATOS PARA EL FRONTEND
    def obtener_datos_para_frontend(self):
        return {
            'recursos': [r.to_dict() for r in self.sistema.recursos],
            'categorias': [c.to_dict() for c in self.sistema.categorias],
            'clientes': [c.to_dict() for c in self.sistema.clientes],
            'configuraciones': [c.to_dict() for c in self.sistema.configuraciones],
            'instancias': [i.to_dict() for i in self.sistema.instancias],
            'consumos': [c.to_dict() for c in self.sistema.consumos]
        }

    #LIMPIAR TODOS LOS DATOS DEL SISTEMA
    def limpiar_datos(self):
        self.sistema = SistemaCloud()
        for archivo in self.archivos.values():
            try:
                if os.path.exists(archivo):
                    os.remove(archivo)
            except Exception as e:
                print(f"Error eliminando {archivo}: {e}")
        
        self.inicializar_archivos()
        return True