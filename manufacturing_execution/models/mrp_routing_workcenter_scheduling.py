# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


# Thêm field ‘alternative_workcenters’ là Công đoạn thay thế vào models ‘mrp.routing.workcenter’.
# Configuration --> Operation
class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    alternative_workcenters = fields.Char(string='Alternative Workcenters', store=True)
