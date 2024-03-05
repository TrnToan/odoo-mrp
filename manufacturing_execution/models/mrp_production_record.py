# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import models, fields, api


class MrpProductionRecord(models.Model):
    _name = 'mrp.production.record'
    _description = 'Production Record'

    workorder_id = fields.Many2one('mrp.workorder', string='Related Work Order', required=True)
    output = fields.Float(string='Output', required=True)
    scrap = fields.Float(string='Scrap', required=True)
    raw_output = fields.Float(string='Raw Output', required=True, _compute='_compute_raw_output', store=False)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=True)

    @api.depends('output', 'scrap')
    def _compute_raw_output(self):
        for record in self:
            record.raw_output = record.output + record.scrap
