# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


# Thêm field ‘mold’ là Khuôn của sản phẩm vào models ‘product.template’.
# Products --> Products
class ProductTemplate(models.Model):
    _inherit = "product.template"

    mold = fields.Char(string="Mold")
