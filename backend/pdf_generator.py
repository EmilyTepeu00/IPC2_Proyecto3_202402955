import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

#GENERAR PDF CON DETALLES
def generar_reporte_factura(numero_factura, factura_data):
    try:
        #Crear directorio de reportes si no hay
        reportes_dir = os.path.join(DATA_DIR, 'reportes')
        os.makedirs(reportes_dir, exist_ok=True)
        
        #Crear nombre de archivo
        filename = f"factura_{numero_factura}.pdf"
        filepath = os.path.join(reportes_dir, filename)
        
        #Crear documento
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        
        #Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        
        #Titulo
        title = Paragraph(f"<b>DETALLE DE FACTURA</b>", title_style)
        elements.append(title)
        
        #Informacion de la factura
        info_data = [
            ['Numero de Factura:', factura_data.get('numero_factura', '')],
            ['Cliente:', f"{factura_data.get('nombre_cliente', '')} ({factura_data.get('nit_cliente', '')})"],
            ['Fecha de Factura:', factura_data.get('fecha_factura', '')],
            ['Periodo Facturado:', f"{factura_data.get('fecha_inicio', '')} a {factura_data.get('fecha_fin', '')}"],
            ['Monto Total:', f"Q {factura_data.get('monto_total', 0):.2f}"]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        #Detalle por instancia
        if factura_data.get('detalle'):
            detalle_title = Paragraph("<b>DETALLE POR INSTANCIA</b>", styles['Heading2'])
            elements.append(detalle_title)
            elements.append(Spacer(1, 10))
            
            for detalle in factura_data.get('detalle', []):
                #Informacion de la instancia
                instancia_data = [
                    [f"Instancia: {detalle.get('instancia_nombre', '')} (ID: {detalle.get('instancia_id', '')})", f"Costo: Q {detalle.get('costo', 0):.2f}"]
                ]
                
                instancia_table = Table(instancia_data, colWidths=[4*inch, 2*inch])
                instancia_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(instancia_table)
                
                #Consumos de la instancia
                if detalle.get('consumos'):
                    consumo_data = [['Fecha y Hora', 'Tiempo (horas)']]
                    for consumo in detalle.get('consumos', []):
                        consumo_data.append([
                            consumo.get('fechahora', ''),
                            f"{consumo.get('tiempo', 0):.2f}"
                        ])
                    
                    consumo_table = Table(consumo_data, colWidths=[3*inch, 2*inch])
                    consumo_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(consumo_table)
                
                elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph("<b>No hay detalles disponibles</b>", styles['Normal']))
        
        #Pie de pagina
        elements.append(Spacer(1, 20))
        footer = Paragraph(f"<i>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Italic'])
        elements.append(footer)
        
        #Generar PDF
        doc.build(elements)
        print(f"PDF generado con exito: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Error generando reporte de factura: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

#GENERAR PDF CON ANALISIS DE VENTAS
def generar_analisis_ventas(fecha_inicio, fecha_fin, tipo_analisis, datos_ventas):
    try:
        #Crear directorio de reportes si no hay
        reportes_dir = os.path.join(DATA_DIR, 'reportes')
        os.makedirs(reportes_dir, exist_ok=True)
        
        #Crear nombre de archivo
        filename = f"analisis_ventas_{fecha_inicio}_{fecha_fin}.pdf"
        filepath = os.path.join(reportes_dir, filename)
        
        #Crear documento
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        
        #Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        
        #Titulo
        titulo = "ANÁLISIS DE VENTAS - CATEGORÍAS Y CONFIGURACIONES" if tipo_analisis == "categorias" else "ANÁLISIS DE VENTAS - RECURSOS"
        title = Paragraph(f"<b>{titulo}</b>", title_style)
        elements.append(title)
        
        #Periodo de analisis
        periodo_data = [
            ['Periodo Analizado:', f"{fecha_inicio} a {fecha_fin}"],
            ['Fecha de Generación:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Total Facturado:', f"Q {datos_ventas.get('total_facturado', 0):.2f}"]
        ]
        
        periodo_table = Table(periodo_data, colWidths=[2*inch, 4*inch])
        periodo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(periodo_table)
        elements.append(Spacer(1, 20))
        
        if tipo_analisis == "categorias":
            #Analisis por categorias y configuraciones
            for categoria in datos_ventas.get('categorias', []):
                cat_title = Paragraph(f"<b>Categoria: {categoria.get('nombre', '')}</b>", styles['Heading2'])
                elements.append(cat_title)
                
                cat_data = [['Configuración', 'Ingresos (Q)', '% del Total']]
                total_categoria = 0
                
                for config in categoria.get('configuraciones', []):
                    ingresos = config.get('ingresos', 0)
                    total_categoria += ingresos
                    porcentaje = (ingresos / datos_ventas.get('total_facturado', 1)) * 100 if datos_ventas.get('total_facturado', 0) > 0 else 0
                    cat_data.append([
                        config.get('nombre', ''),
                        f"{ingresos:.2f}",
                        f"{porcentaje:.1f}%"
                    ])
                
                #Agregar total de la categoria
                cat_data.append([
                    '<b>TOTAL CATEGORÍA</b>',
                    f"<b>{total_categoria:.2f}</b>",
                    f"<b>{(total_categoria / datos_ventas.get('total_facturado', 1)) * 100:.1f}%</b>" if datos_ventas.get('total_facturado', 0) > 0 else "<b>0%</b>"
                ])
                
                cat_table = Table(cat_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                cat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.lightblue),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.darkgrey),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(cat_table)
                elements.append(Spacer(1, 15))
        
        else:
            #Analisis por recursos
            recursos_data = [['Recurso', 'Ingresos (Q)', '% del Total']]
            
            for recurso in datos_ventas.get('recursos', []):
                ingresos = recurso.get('ingresos', 0)
                porcentaje = (ingresos / datos_ventas.get('total_facturado', 1)) * 100 if datos_ventas.get('total_facturado', 0) > 0 else 0
                recursos_data.append([
                    recurso.get('nombre', ''),
                    f"{ingresos:.2f}",
                    f"{porcentaje:.1f}%"
                ])
            
            recursos_table = Table(recursos_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            recursos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(recursos_table)
        
        elements.append(Spacer(1, 20))
        footer = Paragraph(f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Italic'])
        elements.append(footer)
        
        #Generar PDF
        doc.build(elements)
        return filepath
        
    except Exception as e:
        print(f"Error generando analisis de ventas: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None