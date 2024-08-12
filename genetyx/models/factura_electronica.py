from odoo import models, fields

class RucDocumentosTimbrados(models.Model):
    _name = 'ruc.documentos.timbrados'
    _inherit = 'ruc.documentos.timbrados'

    company_name = fields.Char(related='company_id.name', store=True)
