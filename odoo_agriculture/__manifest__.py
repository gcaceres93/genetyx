# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Agriculture / Farm Managment',
    'version': '5.1.2.4',
    'category': 'Services/Project',
    'price': 149.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': "Agriculture / Farm Management Software",
    'description': """ 
Agriculture app
Agriculture Management
Crop Requests
Crops
crop
Agriculture Management Software
Incidents
Dieases Cures
agribusiness
crop yield
agriculture institutes
Farmers
AMS
Farm Locations
farmers
farmer
Agriculture odoo
odoo Agriculture
Agriculture Management System
Animals
print Crop Requests Report
print Crops Report
odoo Agriculture Management Software
Farm Management Software

""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_agriculture/421',#'https://youtu.be/LJwRVOhkK3I',
    'depends': [
               'project',
               'stock',
               'website_customer',
               'maintenance',
               'fleet',
                'animal',
               'paraguay_backoffice',
               # 'partner_ruc'
                ],
    'data':[
        'security/agriculture_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'report/farmer_cropping_request_report.xml',
        'report/farmer_location_crops_report.xml',
        'views/res_partner_view.xml',
        'views/crops_view.xml',
        'views/crops_material_job_view.xml',
        'views/crops_dieases_view.xml',
        'views/project_task_view.xml',
        'views/crops_animals_view.xml',
        'views/google_map_template_view.xml',
        'views/crops_fleet_view.xml',
        'views/crops_incident_view.xml',
        'views/crops_tasks_template_view.xml',
        'views/farmer_cropping_request_view.xml',
        'views/menu_item.xml'
        ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
