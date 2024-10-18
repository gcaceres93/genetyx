
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    animal_ids = fields.One2many('crop.animals', 'dec', string='Animals',
                                 tracking=True)
    animal_count = fields.Integer(compute='_compute_animals_count', string='Toros')
    # Definir la acción para el Smart Button
    def action_view_sales(self):
        sales = self.env['sale.order'].search([('partner_id', '=', self.id)])
        return {
            'name': 'Ventas de ' + self.name,
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sales.ids)],
            'type': 'ir.actions.act_window',
        }
