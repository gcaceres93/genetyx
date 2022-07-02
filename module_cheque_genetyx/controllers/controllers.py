# -*- coding: utf-8 -*-
from odoo import http

# class ModuleChequeGenetyx(http.Controller):
#     @http.route('/module_cheque_genetyx/module_cheque_genetyx/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module_cheque_genetyx/module_cheque_genetyx/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('module_cheque_genetyx.listing', {
#             'root': '/module_cheque_genetyx/module_cheque_genetyx',
#             'objects': http.request.env['module_cheque_genetyx.module_cheque_genetyx'].search([]),
#         })

#     @http.route('/module_cheque_genetyx/module_cheque_genetyx/objects/<model("module_cheque_genetyx.module_cheque_genetyx"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module_cheque_genetyx.object', {
#             'object': obj
#         })