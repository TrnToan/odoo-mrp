# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


# Thêm field ‘alternative_workcenters’ là Công đoạn thay thế vào models ‘mrp.routing.workcenter’.
# Configuration --> Operation
class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    alternative_workcenters = fields.Char(string='Alternative Workcenters', compute='_get_alternative_workcenters', store=False)

    @api.depends('workcenter_id')
    def _get_alternative_workcenters(self):
        for rec in self:
            alternative_workcenter_names = [wc.name for wc in rec.workcenter_id.alternative_workcenter_ids]
            rec.alternative_workcenters = ', '.join(alternative_workcenter_names)
