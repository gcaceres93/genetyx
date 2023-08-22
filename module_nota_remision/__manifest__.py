# -*- coding: utf-8 -*-
{
    'name': "module_nota_remision",

    'summary': """
        Modulo hecho a medida con formato especial.  
        """,

    'description': """
        Este modulo le permite generar una nota de remision con 
        formato personalizado.
    """,

    'author': "Sati",
    'website': "http://www.sati.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Module',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','account','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/stock_picking_view_inherit.xml',
        'reports/template_nota_remision.xml',
        'reports/reports.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}