# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from num2words import num2words
# from odoo.tools import float_round, round

class factura (models.Model):
    _inherit = "account.invoice"

    seccion = fields.Boolean(string="Seccion")
    isrucinternacional = fields.Boolean(string='Imprimir Ruc Internacional',
                                        help="ANTES DE IMPRIMIR DEBE VERIFICAR SI ESTA CARGADO EL RUC INTERNACIONAL EN LA FICHA DEL CLIENTE")
    isredondeo = fields.Boolean(string='Redondeo', help="SE APLICA SOLO AL BANCO CENTRAL DEL PARAGUAY")
    comercial = fields.Many2one('res.partner',string="Comercial")


    # FUNCION PARA EVALUAR LA OPCION POR SECCION
    @api.multi
    def get_seccion(self, seccion):
        seleccion = 0
        if (seccion):
            seleccion = 1
        else:
            seleccion = 0

        return seleccion

    # FUNCION PARA EVALUAR LA LONGITUD DE LAS LINEAS DE PRODUCTOS
    @api.multi
    def get_procesar_producto(self, lista_producto):
        longitud = len(lista_producto)
        print("Londitud: " + str(longitud))
        return longitud

    # FUNCION PARA EVALUAR SI EN LA LINEA DE PRODUCTO INGRESA UNA DECRIPCION DE SECCION
    @api.multi
    def get_descripcion(self, producto):
        descripcion = ''
        if (type(producto.display_type) is str):
            descripcion = producto.name
        return descripcion

    # LA SECCION ES DE TIPO BOOLEAN Y EL NAME ES STR ESO EVALUAMOS PARA ACUMULAR EL PRECIO
    @api.multi
    def get_prueba(self, tipo):
        tipo = type(tipo)
        bandera = 0
        if (tipo is str):
            bandera = 1
        elif (tipo is True):
            bandera = 0
        elif (tipo is False):
            bandera = 0
        # print(tipo)
        print(bandera)
        return bandera

    def get_tipo(self, tipo):
        bandera = 0
        if 'line_section' in tipo:
            bandera = 1
        elif 'line_nota' in tipo:
            bandera = 0
        return bandera

    @api.multi
    def get_total_precio(self, cantidad, precio_unitario):
        if cantidad > 0:
            cant_entero = int(cantidad)
            # precio_total = cant_entero * precio_unitario
            precio_total = cantidad * precio_unitario
            return precio_total
        else:
            precio_total = cantidad * precio_unitario
            return precio_total

    @api.multi
    def get_redondeo_iva(self, iva, moneda):
        if 'PYG' in moneda:
            # redondeo_parcial = round(iva, 1)
            redondeo_total = round(iva)
            return redondeo_total
        elif 'USD' in moneda:
            return iva

    @api.multi
    def get_redondeo(self, acumulador_impuesto, moneda):
        if 'PYG' in moneda:
            # redondeo_parcial = round(acumulador_impuesto,1)
            # redondeo_total = round(redondeo_parcial)
            redondeo = round(acumulador_impuesto, 1)
            return redondeo
        elif 'USD' in moneda:
            redondeo = acumulador_impuesto
            # redondeo = round(acumulador_impuesto,2)
            return redondeo

    @api.multi
    def get_pos(self):
        pos = self.env['pos.order'].search([('name', '=', self.reference)])
        return pos

    @api.multi
    def get_monto(self, impuesto):
        i = 0
        j = 0
        entero = 0
        if (self.currency_id.id == 3):
            impuesto_letra = str(impuesto)
            while i < len(impuesto_letra):
                if (impuesto_letra[i] == "."):
                    j = i + 3
                    break;
                i += 1
            return impuesto_letra[:j]
        else:
            entero = int(impuesto)
        return entero

    # termino_pago=fields.Integer(compute="_get_termino_pago")
    #
    # @api.depends
    # def _get_termino_pago(self):
    #     fecha_factura=int(self.date_invoice)
    #     fecha_vencimiento=int(self.date_due)
    #     return fecha_factura - fecha_vencimiento

    def get_invoice_data(self):
        invoice = self
        datos = list()
        print(invoice)
        dato_final = 'None'
        for orden in invoice:
            datos.append(orden.nro_factura)
            datos.append(orden.talonario_factura.name)
            datos.append(orden.talonario_factura.fecha_inicio)
            datos.append(orden.talonario_factura.fecha_final)
            dato_final = orden.talonario_factura.name
            print(orden.talonario_factura.name)
            print(datos)

        return datos

    def sacacoma(self, n):
        return int(n)

    @api.multi
    def tipofactura(self, n):
        if (n == 2):
            return 'Credito'
        elif (n == 1):
            return 'Contado'

    @api.multi
    def calcular_letras(self, numero):
        letras = self.monto_en_letras = num2words(numero, lang='es').upper()
        letras = '--' + 'GUARANIES ' + letras + '--'
        return letras

    @api.multi
    def calcular_letras_dolar(self, numero):
        nuevo_numero = str(numero).split('.')
        entero = num2words(int(nuevo_numero[0]), lang='es').upper()
        # if len(nuevo_numero[1] == 1):
        if len(nuevo_numero[1]) == 1:
            if nuevo_numero[1] == '0':
                decimal = num2words(int(nuevo_numero[1]), lang='es').upper()
            else:
                decimal = num2words(int(nuevo_numero[1] + '0'), lang='es').upper()
        else:
            decimal = num2words(int(nuevo_numero[1]), lang='es').upper()
        letras = entero + ' DOLARES ' + ' CON ' + decimal + ' CENTAVOS '
        return letras

    @api.multi
    # def agregar_punto_de_miles(self, numero):
    #     numero_con_punto = '.'.join([str(int(numero))[::-1][i:i + 3] for i in range(0, len(str(int(numero))), 3)])[::-1]
    #     return numero_con_punto

    def agregar_punto_de_miles(self, numero, moneda):
        entero = int(numero)
        if 'USD' in moneda:

            decimal = '{0:.2f}'.format(numero - entero)
            entero_string = '.'.join([str(int(entero))[::-1][i:i + 3] for i in range(0, len(str(int(entero))), 3)])[
                            ::-1]
            if decimal == '0.00':
                numero_con_punto = entero_string + ',00'
            else:
                decimal_string = str(decimal).split('.')
                numero_con_punto = entero_string + ',' + decimal_string[1]
        elif 'PYG' in moneda:
            numero_con_punto = '.'.join([str(int(numero))[::-1][i:i + 3] for i in range(0, len(str(int(numero))), 3)])[
                               ::-1]
            return numero_con_punto
        else:
            numero_con_punto = '.'.join([str(int(numero))[::-1][i:i + 3] for i in range(0, len(str(int(entero))), 3)])[
                               ::-1]
        num_return = numero_con_punto
        return num_return

    def calcula_moneda(self, moneda):
        if 'USD' in moneda:
            return '$'
        elif 'PYG' in moneda:
            return 'Gs.'



