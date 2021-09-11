# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Inventory Adjustment Cancel/Reverse Odoo",
    'version': "13.0.0.2",
    'category': "Warehouse",
    'summary': 'Apps for cancel inventory adjustment cancel reverse inventory adjustment reverse revert inventory adjustment revert stock picking cancel picking order cancel delivery order cancel stock move cancel done inventory cancel done inventory revert done inventory',
    'description': """

    This module helps to reverse inventory adjustments allow to cancel inventory on done stage and reset inventory on cancel stage

odoo stock inventory reverse workflow stock inventory cancel inventory adjustment cancel incoming shipment cancel 
odoo cancel inventory adjustment cancel delivery order cancel incoming shipment cancel order set to draft picking cancel done picking revese picking process 
odoo cancel done delivery order reverse delivery order stock inventory adjustment reverse workflow stock inventory adjustment cancel
odoo stock adjustment reverse workflow warehouse stock cancel stock warehouse cancel cancel stock for inventory cancel stock inventory cancel inventory adjustment from done state 
odoo cancel warehouse stock adjustment cancel order set to draft picking cancel done picking revese picking process cancel done delivery order. 
odoo orden de entrega inversa sélection de stock reverse workflow sélection de stock annuler 
annulation de commande annulation de livraison annulation de commande annulation de livraison annulation de livraison
 annulation de la commande annulation de la sélection annulation de la préparation annulation du bon de livraison. ordre de livraison inverse.
 odoo cancel stock Inventory Adjustment cancel and reset to draft Inventory Adjustment odoo cancel reset Inventory Adjustment 
 odoo cancel Inventory Adjustment cancel delivery stock Adjustment cancel stock Adjustment
odoo reverse Inventory Adjustment reverse stock Inventory Adjustment
odoo cancel orders order cancel odoo cancel picking odoo cancel stock move odoo stock move cancel
odoo Inventory Adjustment Cancel Cancel Inventory Adjustment delivery cancel
odoo picking cancel Reverse order reverse picking reverse delivery reverse shipment

    """,
    'author': "BrowseInfo",
    'website' : "www.browseinfo.in",
    'price': 35.00,
    'currency': "EUR",
    'depends': ['stock'],
    'data': [
        "security/ir.model.access.csv",
        "security/inventory_adjustment_group.xml",
        "views/inventory_adjustment_view.xml"
    ],
    'qweb': [
    ],
    'auto_install': False,
    'installable': True,
    'live_test_url':"https://youtu.be/gAuSrPqwQtk",
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
