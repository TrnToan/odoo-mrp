# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


# Thêm field ‘mold’ là Khuôn của sản phẩm vào models ‘product.template’.
# Products --> Products
class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Bỏ trường mold và thay bằng get_mold lấy từ ResourceNetworkConnection
    mold = fields.Char(string="Mold")
    get_required_mold = fields.Char(string="Related Mold", compute='_get_mold_from_resource_network_connection')
    product_template_property_ids = fields.One2many('product.template.property', 'product_template_id',
                                                    string="Product Template Properties")
    product_product_ids = fields.One2many('product.product', 'product_tmpl_id', string="Product Products")

    @api.depends('name')
    def _get_mold_from_resource_network_connection(self):
        for rec in self:
            rec.get_required_mold = (rec.env['resource.network.connection']
                                     .search([('from_resource_id', '=', rec.name)])
                                     .to_resource_id)
