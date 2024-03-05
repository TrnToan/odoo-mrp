# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import api, fields, models


class ProductCategoryGroup(models.Model):
    _name = "product.category.group"
    _description = "Product Category Group"

    name = fields.Char(string="Product Category Group", required=True)
    product_category_ids = fields.One2many('product.category', 'product_category_group_id', string="Product Categories")
