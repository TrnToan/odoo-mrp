# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Manufacturing Execution',
    'version': '1.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Manufacturing Execution System',
    'description': """Manufacturing Execution System""",
    'depends': ['base', 'sale', 'mrp', 'product', 'web_timeline'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/planning_date_start_view.xml',
        'wizard/scheduling_date_start_view.xml',
        'views/mrp_production_scheduling.xml',
        'views/res_partner_scheduling.xml',
        'views/product_template_scheduling.xml',
        'views/sale_order_scheduling.xml',
        'views/mrp_routing_workcenter_scheduling.xml',
        'views/mrp_workorder_scheduling.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
