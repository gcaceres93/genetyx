# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from num2words import num2words
# from odoo.tools import float_round, round

class stock_move_class (models.Model):
    _inherit = "stock.move"

    def _do_unreserve(self):
        moves_to_unreserve = self.env['stock.move']
        for move in self:
            # if move.state == 'cancel':
            #     # We may have cancelled move in an open picking in a "propagate_cancel" scenario.
            #     continue
            if move.state == 'done':
                if move.scrapped:
                    # We may have done move in an open picking in a scrap scenario.
                    continue
                else:
                    raise UserError(_('No puedes desreservar movimientos en estado \'Hecho\'.'))
            moves_to_unreserve |= move
        moves_to_unreserve.with_context(prefetch_fields=False).mapped('move_line_ids').unlink()