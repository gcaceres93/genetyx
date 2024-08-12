# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DocumentosTimbrados(models.Model):
    _inherit = 'ruc.documentos.timbrados'

    def _compute_required_tipo_documento(self):
        for record in self:
            if self.env.user.company_id.name == "GENETYX S.A":
                record.tipo_documento_required = True
            else:
                record.tipo_documento_required = False

    tipo_documento_required = fields.Boolean(string="Requiere Tipo Documento Electrónico", compute='_compute_required_tipo_documento')

    tipo_documento_electronico = fields.Selection([
        ('1', 'Factura electrónica'),
        ('2', 'Factura electrónica de exportación'),
        ('3', 'Factura electrónica de importación'),
        ('4', 'Autofactura electrónica'),
        ('5', 'Nota de crédito electrónica'),
        ('6', 'Nota de débito electrónica'),
        ('7', 'Nota de remisión electrónica'),
        ('8', 'Comprobante de retención electrónico'),
    ], string='Tipo Documento Electrónico', required=False)

    @api.onchange('tipo_documento_required')
    def _onchange_tipo_documento_required(self):
        for record in self:
            if record.tipo_documento_required:
                record._fields['tipo_documento_electronico'].required = True
            else:
                record._fields['tipo_documento_electronico'].required = False
