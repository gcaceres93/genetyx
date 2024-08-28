from odoo import models, fields

class AnimalRaza(models.Model):
    _name = 'raza'


    raza = fields.Char(string='Raza', required=True)
    color =  fields.Selection(
        [('marron', 'Marron'), ('negro', 'Negro'),('blanco', 'Blanco')],
        default="negro",
        string='Color', required=False, tracking=True)