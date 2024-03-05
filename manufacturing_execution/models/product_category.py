# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    product_template_ids = fields.One2many('product.template', 'categ_id', string="Products")
    product_category_group_id = fields.Many2one('product.category.group', string="Group")

