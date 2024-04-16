# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


# Thêm field ‘mold’ là Khuôn của sản phẩm vào models ‘product.template’.
# Products --> Products
class ProductTemplate(models.Model):
    _inherit = "product.template"

    get_required_mold = fields.Char(string="Related Mold", compute='_get_mold_from_resource_network_connection')
    mold = fields.Char(string="Mold", help="The mold used to produce this product", required=True)
    product_template_property_ids = fields.One2many('product.template.property', 'product_template_id',
                                                    string="Product Template Properties")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Product name must be unique'),
        ('default_code_uniq', 'unique(default_code)', 'Product internal reference must be unique')
    ]

    @api.depends('name')
    def _get_mold_from_resource_network_connection(self):
        for rec in self:
            mold = rec.env['resource.network.connection'].search([('from_resource_id', '=', rec.name),
                                                                  ('connection_type', '=', 'product_mold')], limit=1)
            if mold:
                rec.get_required_mold = mold.to_resource_id

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        mold = vals.get('mold')
        if not self.check_mold_existence(mold):
            raise ValueError(f"Mold {mold} does not exist")

        self.env['resource.network.connection'].create({
            'from_resource_id': vals.get('name'),
            'to_resource_id': vals['mold'],
            'connection_name': f"{vals.get('name')} is molded from {vals['mold']}",
            'connection_type': 'product_mold'
        })
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'mold' in vals:
            mold = vals.get('mold')
            if not self.check_mold_existence(mold):
                raise ValueError(f"Mold {mold} does not exist")

            (self.env['resource.network.connection'].search([('from_resource_id', '=', self.name),
                                                            ('connection_type', '=', 'product_mold')])
                                                    .write(
                {
                    'to_resource_id': vals['mold'],
                    'connection_name': f"{self.name} is molded from {vals['mold']}"
                }
            ))
        return res

    def check_mold_existence(self, mold):
        if not self.env['equipment.equipment'].search([('name', '=', mold)]):
            return False
        return True
