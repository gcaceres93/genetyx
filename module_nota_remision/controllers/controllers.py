# -*- coding: utf-8 -*-
from odoo import http

# class ModuleNotaRemision(http.Controller):
#     @http.route('/module_nota_remision/module_nota_remision/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module_nota_remision/module_nota_remision/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('module_nota_remision.listing', {
#             'root': '/module_nota_remision/module_nota_remision',
#             'objects': http.request.env['module_nota_remision.module_nota_remision'].search([]),
#         })

#     @http.route('/module_nota_remision/module_nota_remision/objects/<model("module_nota_remision.module_nota_remision"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module_nota_remision.object', {
#             'object': obj
#         })