# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import models, fields, api


class MrpProductionRecord(models.Model):
    _name = 'mrp.production.record'
    _description = 'Production Record'

    workorder_id = fields.Many2one('mrp.workorder', string='Related Work Order', required=True)
    output = fields.Float(string='Current Output', required=True, help="The number of products produced that meets the standard")
    scrap = fields.Float(string='Current Scrap', required=True, help="The number of products that are not up to standard")
    raw_output = fields.Float(string='Current Raw Output', required=True, compute='_compute_raw_output')
    # A product is produced after each cycle
    cycle_start_time = fields.Datetime(string='Start Time', required=True, help="The time when the cycle started")
    cycle_end_time = fields.Datetime(string='End Time', required=True, help="The time when the cycle ended")
    injection_time = fields.Float(string='Injection Time', required=True, help="The time for injection process")

    @api.depends('output', 'scrap')
    def _compute_raw_output(self):
        for record in self:
            record.raw_output = record.output + record.scrap
