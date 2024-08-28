# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class FarmerCroppingRequest(models.Model):
    _name = 'farmer.cropping.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _description = "Crop Requests"

    number = fields.Char(
        string='Number',
        readonly=True,
        copy=False
    )
    name = fields.Char(
        string='Name',
        required=True
    )
    description = fields.Text(
        string='Description'
    )
    internal_note = fields.Text(
        string='Internal Notes'
    )
    state = fields.Selection([
        ('new', 'New'),
        ('confirm', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done','Done'),
        ('cancel','Cancel')
        ],
        string="State",
        default='new',
        required=True
    )
    start_date = fields.Date(
        string='Start Date',
        required=True
    )
    end_date = fields.Date(
        string='End Date',
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id
    )
    user_id = fields.Many2one(
        'res.users',
        string="Supervisor",
        default=lambda self: self.env.user,
        required=True
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        copy=False
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string="Responsible User",
        default=lambda self: self.env.user,
        required=True,
    )
    crop_ids = fields.Many2one(
        'farmer.location.crops',
        string='Crop',
        required=True
    )
    task_count = fields.Integer(
        compute='_compute_task_counter',
        string="Task Count"
    )
    equipment_count = fields.Integer(
        compute='_compute_equipment_counter',
        string="Equipment Count"
    )
    animal_count = fields.Integer(
        compute='_compute_animal_counter',
        string="Animal Count"
    )
    dieases_count = fields.Integer(
        compute='_compute_dieases_counter',
        string="Dieases Count"
    )
    fleet_count = fields.Integer(
        compute='_compute_fleet_counter',
        string="Fleet Count"
    )
    project_count = fields.Integer(
        compute='_compute_project_counter',
        string="Project Count"
    )

    def _compute_task_counter(self):
        for rec in self:
            rec.task_count = self.env['project.task'].search_count([('project_id','in', self.project_id.ids)])

    def _compute_project_counter(self):
        for rec in self:
            rec.project_count = self.env['project.project'].search_count([('id', 'in', self.project_id.ids)])
            
    
    def _compute_fleet_counter(self):
        fleets = []
        for rec in self:
            rec.fleet_count = 0 # odoo13
            for crop in rec.crop_ids:
                for crop_temp in crop.crop_task_ids:
                    for fleet in crop_temp.fleet_ids:
                        fleets.append(fleet.id)
                        rec.fleet_count = self.env['crops.fleet'].search_count([('id','in', fleets)])

    def _compute_dieases_counter(self):
        dieaseses = []
        for rec in self:
            rec.dieases_count = 0 # odoo13
            for crop in rec.crop_ids:
                for dieases in crop.crops_dieases_ids:
                    dieaseses.append(dieases.id)
                    rec.dieases_count = self.env['crops.dieases'].search_count([('id','in', dieaseses)])

    def _compute_equipment_counter(self):
        equipments = []
        for rec in self:
            rec.equipment_count = 0 # odoo13
            for crop in rec.crop_ids:
                for crop_temp in crop.crop_task_ids:
                    for equipment in crop_temp.equipment_ids:
                        equipments.append(equipment.id)
                        rec.equipment_count = self.env['maintenance.equipment'].search_count([('id','in', equipments)])
    
    def _compute_animal_counter(self):
        animals = []
        for rec in self:
            rec.animal_count = 0 # odoo13
            for crop in rec.crop_ids:
                for crop_temp in crop.crop_task_ids:
                    for animal in crop_temp.animal_ids:
                        animals.append(animal.id)
                        rec.animal_count = self.env['crops.animals'].search_count([('id','in', animals)])
    
    # @api.multi #odoo13
    def view_project_request(self):
        action = self.env.ref('odoo_agriculture.action_view_farmer_cropping_project').sudo().read()[0]
        action['domain'] = [('id','in', self.project_id.ids)]
        return action

    # @api.multi #odoo13
    def view_task_request(self):
        action = self.env.ref('odoo_agriculture.action_view_farmer_cropping_task').sudo().read()[0]
        action['domain'] = [('project_id','in', self.project_id.ids)]
        return action

    
    # @api.multi #odoo13
    def view_animal_request(self):
        action = self.env.ref('odoo_agriculture.action_crops_animals').sudo().read()[0]
        animals = []
        for rec in self:
            for crop in rec.crop_ids:
                for crop_temp in crop.crop_task_ids:
                    for animal in crop_temp.animal_ids:
                        animals.append(animal.id)
        action['domain'] = [('id','in', animals)]
        return action


    # @api.multi #odoo13
    def view_fleet_request(self):
        action = self.env.ref('odoo_agriculture.action_crops_fleet_act').sudo().read()[0]
        fleets = []
        for rec in self:
            for crop in rec.crop_ids:
                for crop_temp in crop.crop_task_ids:
                    for fleet in crop_temp.fleet_ids:
                        fleets.append(fleet.id)
        action['domain'] = [('id','in', fleets)]
        return action

    # @api.multi #odoo13
    def view_dieases_request(self):
        action = self.env.ref('odoo_agriculture.action_crops_dieases').sudo().read()[0]
        dieaseses = []
        for rec in self:
            for crop in rec.crop_ids:
                for dieases in crop.crops_dieases_ids:
                    dieaseses.append(dieases.id)
        action['domain'] = [('id','in', dieaseses)]
        return action

    # @api.multi #odoo13
    def view_equipment_request(self):
        action = self.env.ref('maintenance.hr_equipment_action').sudo().read()[0]
        equipments = []
        for rec in self:
            for crop in rec.crop_ids:
                for crop_temp in crop.crop_task_ids:
                    for equipment in crop_temp.equipment_ids:
                        equipments.append(equipment.id)
        action['domain'] = [('id','in', equipments)]
        return action

    @api.model
    def create(self, vals): 
        vals['number'] = self.env['ir.sequence'].next_by_code('farmer.cropping.request')
        return super(FarmerCroppingRequest,self).create(vals)

    # @api.multi #odoo13
    # def action_in_progress(self,vals):
    def action_in_progress(self , vals=None): #odoo13
        self.write({'state': 'in_progress'})
        project_vals = {
            'name': self.name + '-' + self.number,
            'company_id': self.company_id.id,
            'alias_id': 1,
            'custom_request_id': self.id
                }
        project_id = self.env['project.project'].create(project_vals)
        for rec in self:
            rec.project_id = project_id.id
            crop_ids = rec.crop_ids
            crop_task_ids = crop_ids.mapped('crop_task_ids')

            my_dict = {}
            for x in crop_task_ids:
                my_dict[x.task_id] = x
            task_ids = crop_task_ids.mapped('task_id')
            result = []
            old = {}
            pp = []
            for task in task_ids:
                default = {
                            'project_id': project_id.id,
                            'name' : task.name + '-' + rec.number,
                            'custom_request_id': rec.id,
                            'is_cropping_request': True,
                           }
                duplicate_task_ids = task.copy(default)
                old[duplicate_task_ids.id] = task
                pp.append(duplicate_task_ids)
            for d in pp:
                equipment_lst = []
                myfav_task = old[d.id]
                for x1 in my_dict[old[d.id]].equipment_ids:
                    equipment_lst.append(x1.id)
                for mm in my_dict[old[d.id]].animal_ids:
                    default = {'crops_tasks_template_id':False, 'task_id':d.id}
                    fu = mm.copy(default)
                for fff in my_dict[old[d.id]].fleet_ids:
                    default = {'crops_tasks_template_id':False, 'task_id':d.id}
                    fu1 = fff.copy(default)
                d.equipment_ids = equipment_lst

    # @api.multi #odoo13
    def action_confirm(self):
        return self.write({'state': 'confirm'})

    # @api.multi #odoo13
    def action_done(self):
        return self.write({'state': 'done'})

    # @api.multi #odoo13
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    # @api.multi #odoo13
    def action_reset_to_draft(self):
        return self.write({'state': 'new'})

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


