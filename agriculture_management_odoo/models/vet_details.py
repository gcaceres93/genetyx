# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, api


class VetDetails(models.Model):
    _name = 'vet.details'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = 'Vet Details'
    _rec_name = 'vet_name'

    vet_name = fields.Many2one('res.partner', string='Veterinario', required=True,
                                  tracking=True)
    vet_name_image = fields.Binary(string='Image', tracking=True)
    note = fields.Text(string='Notes', tracking=True)

    @api.onchange('vet_name')
    def onchange_farmer_name(self):
        if self.vet_name:
            self.vet_name_image = self.vet_name.image_1920
