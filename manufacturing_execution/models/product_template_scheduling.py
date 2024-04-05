# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


# Thêm field ‘mold’ là Khuôn của sản phẩm vào models ‘product.template’.
# Products --> Products
class ProductTemplate(models.Model):
    _inherit = "product.template"

    get_required_mold = fields.Char(string="Related Mold", compute='_get_mold_from_resource_network_connection')
    product_template_property_ids = fields.One2many('product.template.property', 'product_template_id',
                                                    string="Product Template Properties")

    @api.depends('name')
    def _get_mold_from_resource_network_connection(self):
        for rec in self:
            mold = rec.env['resource.network.connection'].search([('from_resource_id', '=', rec.name),
                                                                  ('connection_type', '=', 'product_mold')], limit=1)
            if mold:
                rec.get_required_mold = mold.to_resource_id
