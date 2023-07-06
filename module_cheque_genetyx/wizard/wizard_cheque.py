# -*- coding: utf-8 -*-

from odoo import fields, models, exceptions, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import time
from num2words import num2words
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class WizardCheque(models.TransientModel):

    _name='genetyx.wizard.cheque'

    cheque = fields.Many2many('account.check',string="Cheque",size=4)

    @api.onchange('cheque')
    def verificar(self):
        print("len cheque",len(self.cheque))
        if len(self.cheque) > 4:
            raise ValidationError("SOLO PUEDE IMPRIMIR HASTA CUATRO")

    def ordenar_cheque_por_numero(self):
        if self.cheque:
            ordenados_por_nombre = self.cheque.sorted(key=lambda r: (r.name))
            return ordenados_por_nombre

    
    def report_cheque(self):
        if self.cheque:
            self.ensure_one()
            self.sent = True
            return self.env.ref('module_cheque_genetyx.report_cheque_genetyx').report_action(self)

    
    def agregar_punto_de_miles(self, numero, moneda):
        entero = int(numero)
        if 'USD' in moneda:

            decimal = '{0:.2f}'.format(float_round(numero, precision_rounding=0.01, rounding_method='HALF-UP') - entero)
            entero_string = '.'.join([str(int(entero))[::-1][i:i + 3] for i in range(0, len(str(int(entero))), 3)])[
                            ::-1]
            if decimal == '0.00':
                numero_con_punto = entero_string + ',00'
            else:
                decimal_string = str(decimal).split('.')
                numero_con_punto = entero_string + ',' + decimal_string[1]
        elif 'PYG' in moneda:
            # return entero
            numero_con_punto = '.'.join([str(int(float_round(numero, precision_rounding=1, rounding_method='HALF-UP')))[::-1][i:i + 3] for i in range(0, len(str(int(entero))), 3)])[
                               ::-1]
            num_return = numero_con_punto
        else:
            numero_con_punto = '.'.join([str(int(float_round(numero, precision_rounding=0.01, rounding_method='HALF-UP')))[::-1][i:i + 3] for i in range(0, len(str(int(entero))), 3)])[
                               ::-1]
        num_return = numero_con_punto
        return num_return

    def cantidaddecaracteres70(self, a_nombre_de):
            b = str(a_nombre_de)
            return b[0:70]

    def cantidaddecaracteres24(self, a_nombre_de):
        b = str(a_nombre_de)
        return b[0:24]

    def cantidaddecaracteres35(self, a_nombre_de):
        b = str(a_nombre_de)
        return b[0:45]

    
    def calcular_letras(self, numero):
        entero = int(numero)
        letras = num2words(entero, lang='es').upper()
        # letras = '--'+'GUARANIES ' + letras + '--'
        letras = letras + '.-'
        return letras


    
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
        letras = entero + ' CON ' + decimal + ' CENTAVOS.-'
        return letras

    def dia(self, fecha):
        cadena = str(fecha)
        return cadena[8:10]

    def mes(self, fecha):
        cadena = str(fecha)
        return cadena[5:7]

    def ano(self, fecha):
        cadena = str(fecha)
        return cadena[2:4]

    def longitud(self,a):
        return len(a)
