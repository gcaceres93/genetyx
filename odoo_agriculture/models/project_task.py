# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class Task(models.Model):
    _inherit = "project.task"

    crop_incident_ids = fields.One2many(
        'crops.incident',
        'task_id',
        string='Crops Incident'
    )
    animal_ids = fields.One2many(
        'crops.animals',
        'task_id',
        string="Animals",
        required=False
    )
    fleet_ids = fields.One2many(
        'crops.fleet',
        'task_id',
        string="Fleets",
        required=False
    )
    equipment_ids = fields.Many2many(
        'maintenance.equipment',
        string='Equipments',
        required=False
    )
    custom_request_id = fields.Many2one(
        'farmer.cropping.request',
        string = 'Crop Request'
    )
    is_cropping_request = fields.Boolean(
        string='Is Cropping Request?',
    )


class Project(models.Model):
    _inherit = "project.project"

    custom_request_id = fields.Many2one(
        'farmer.cropping.request',
        string = 'Crop Request'
    )
    crop_request_count = fields.Integer(
        compute='_compute_crop_request_counter',
        string="Crop Request Count"
    )
    crop_count = fields.Integer(
        compute='_compute_crop_counter',
        string="Crop Count"
    )

    # @api.multi #odoo13
    def action_crops_requests(self):
        action = self.env.ref('odoo_agriculture.action_farmer_cropping_request').sudo().read()[0]
        action['domain'] = [('project_id','in', self.ids)]
        return action

    def _compute_crop_request_counter(self):
        for rec in self:
            rec.crop_request_count = self.env['farmer.cropping.request'].search_count([('project_id', 'in', self.ids)])

    # @api.multi #odoo13
    def action_crops(self):
        action = self.env.ref('odoo_agriculture.action_farmer_location_crop').sudo().read()[0]
        action['domain'] = [('id','=', self.custom_request_id.crop_ids.id)]
        return action

    def _compute_crop_counter(self):
        for rec in self:
            rec.crop_count = self.env['farmer.location.crops'].search_count([('id', '=', rec.custom_request_id.crop_ids.id)])

    #@api.model
    #def create(self, vals): 
        ##vals['number'] = self.env['ir.sequence'].next_by_code('project.project')
    #    return super(Project,self).create(vals)

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

