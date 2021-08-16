# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from num2words import num2words
# from odoo.tools import float_round, round

class factura (models.Model):
    _inherit = "account.invoice"

    seccion = fields.Boolean(string="Seccion")

    @api.multi
    def get_seccion(self, seccion):
        seleccion = 0
        if (seccion):
            seleccion = 1
        else:
            seleccion = 0

        return seleccion


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
