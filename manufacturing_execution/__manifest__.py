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
        'wizard/product_template_import_view.xml',
        'views/mrp_production_scheduling.xml',
        'views/res_partner_scheduling.xml',
        'views/product_template_scheduling.xml',
        'views/sale_order_scheduling.xml',
        'views/mrp_routing_workcenter_scheduling.xml',
        'views/mrp_workorder_scheduling.xml',
        'views/mrp_resource_management.xml',
        'views/mrp_workcenter_inherited_view.xml',
        'views/mrp_site.xml',
        'views/mrp_area.xml',
        'views/res_company.xml',
        'views/product_management.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
