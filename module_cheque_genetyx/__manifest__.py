# -*- coding: utf-8 -*-
{
    'name': "module_cheque_genetyx",

    'summary': """
        Modulo con diseño estandar pre-impresa de cheque guaranies y dolares. 
        """,

    'description': """
        Podra imprimir cheques en guaranies y dolares a modo de agilizar la operacion de la carga de datos en cheques fisicos.
    """,

    'author': "Sati",
    'website': "http://sati.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Module',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_check',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_check_view_inherit.xml',
        'reports/reports.xml',
        'reports/template_cheque.xml',
        'reports/template_cheque_dolar.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}