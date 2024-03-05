# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import api, fields, models


class ProductTemplateProperty(models.Model):
    _name = 'product.template.property'
    _description = 'Product Template Property'

    property_name = fields.Char(string="Property Name", required=True)
    property_value = fields.Char(string="Property Value", required=True)
    product_template_id = fields.Many2one('product.template', string="Product Template")
