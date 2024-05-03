# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    get_required_mold = fields.Char(string="Related Mold", compute='_get_mold_from_resource_network_connection')
    product_template_property_ids = fields.One2many('product.template.property', 'product_template_id',
                                                    string="Product Template Properties")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Product name must be unique'),
        ('default_code_uniq', 'unique(default_code)', 'Product internal reference must be unique')
    ]
