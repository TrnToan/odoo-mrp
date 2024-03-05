# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


# Thêm field ‘mold’ là Khuôn của sản phẩm vào models ‘product.template’.
# Products --> Products
class ProductTemplate(models.Model):
    _inherit = "product.template"

    mold = fields.Char(string="Mold")
    product_template_property_ids = fields.One2many('product.template.property', 'product_template_id',
                                                    string="Product Template Properties")
    product_product_ids = fields.One2many('product.product', 'product_tmpl_id', string="Product Products")
