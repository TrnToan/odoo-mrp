# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


# Configuration --> Operation
class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    alternative_workcenters = fields.Char(string='Alternative Workcenters', store=True)
    mold = fields.Char(string='Mold', help='The mold used to produce this product', store=True)
