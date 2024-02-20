# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


# Thêm field ‘weight’ là trọng số của khách hàng vào model ‘res.partner’.
class Partner(models.Model):
    _inherit = "res.partner"

    weight = fields.Float(string='Weight', store=True)
