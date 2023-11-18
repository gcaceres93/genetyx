# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from num2words import num2words

class notaRemision(models.Model):
    _inherit = "stock.picking"
    fecha_estimada = fields.Datetime(string="Fecha Emisión: ", compute='compute_getFechaEmision', readonly=False)
    # fecha_estimada=fields.Datetime(string="Fecha Emisión: ")
    punto_de_partida = fields.Char(string="Punto De Partida: ", compute='compute_getPuntoPartida')
    # punto_de_partida = fields.Char(string="Punto De Partida: ")
    punto_de_llegada = fields.Char(string="Punto De Llegada: ", compute='compute_getPuntoLlegada', readonly=False)
    # punto_de_llegada = fields.Char(string="Punto De Llegada: ")
    #nro_factura = fields.Char(string="Número Fctura: ", related="sale_id.invoice_ids.nro_factura")
    nro_factura = fields.Char(string="Número Fctura: ")


    #
    #
    # marca_vehiculo=fields.Char(string="Marca Vehiculo Transporte")
    # nombre_transportista=fields.Char(string="Nombre Razon Social Transp")
    # ruc_transportista=fields.Char("RUC Transp")
    # direccion_partida=fields.Char(string="Direccion de Partida")
    # ciudad_partida=fields.Char(string="Ciudad de Partida")
    # direccion_llegada=fields.Char(string="Direccion de Llegada")
    # ciudad_llegada=fields.Char(string="Ciudad de Llegada")
    # inicio_traslado=fields.Date(string="Inicio de Traslado")
    # fin_traslado=fields.Date(string="Fin de Traslado")
    # km_recorrido=fields.Char(string="KM Recorrido")
    # chapa1_numero=fields.Char(string="Chapa Nro.")
    # chapa2_numero=fields.Char(string="Chapa Nro.")
    # nombre_conductor=fields.Char(string="Nombre del Cond.")
    # ci_conductor=fields.Char(string="C.I. del Cond.")
    # motivo_traslado=fields.Char(string="Motivo De Tras.")
    # comprobante_venta=fields.Char(string="Comprob. De Venta")
    # timbrado_numero=fields.Char(string="Timbrado Nro.")
    # direccion_conductor=fields.Char(string="Direccion del Cond.")
# testing para gitcc
    @api.depends('state')
    def compute_getFechaEmision(self):
        for rec in self:
            rec.fecha_estimada = rec.scheduled_date

    @api.depends('state')
    def compute_getPuntoPartida(self):
        for rec in self:
            if rec.company_id.street and rec.company_id.street2:
                rec.punto_de_partida = rec.company_id.street + ' , ' + rec.company_id.street2
            else:
                rec.punto_de_partida = rec.company_id.street

    #
    @api.depends('state')
    def compute_getPuntoLlegada(self):
        for rec in self:
            if rec.partner_id.street and rec.partner_id.street2:
                rec.punto_de_llegada = rec.partner_id.street + ' , ' + rec.partner_id.street2
            else:
                rec.punto_de_llegada = rec.partner_id.street
