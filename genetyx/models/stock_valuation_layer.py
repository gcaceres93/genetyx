from odoo import models, fields

class CustomStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    product_id = fields.Many2one('product.product', 'Product', readonly=False,  required=True, check_company=True, auto_join=True)
    unit_cost = fields.Float('Unit Value', readonly=False)
    value = fields.Monetary('Total Value', readonly=False)
    company_id = fields.Many2one('res.company', readonly=False, required = True)
    quantity = fields.Float('Quantity', help='Quantity', readonly=False, digits='Product Unit of Measure')