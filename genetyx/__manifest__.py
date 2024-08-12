# -*- coding: utf-8 -*-
{
    'name': "genetyx",

    'summary': """
        Modulo genetyx""",

    'description': """
        Modulo genetyx
    """,

    'author': "SATI S.A.",
    'website': "http://www.sati.com.py",
    'license': 'LGPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','stock','sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/menu.xml',
        'views/account_invoice.xml',
        'views/factura_electronica.xml',
        'reports/factura_report.xml',
        'reports/nota_de_credito_report.xml',
        'reports/genetyx_reports.xml'
    ],
}



