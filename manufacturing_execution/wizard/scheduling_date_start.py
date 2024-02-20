# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SchedulingDateStart(models.TransientModel):
    _name = 'scheduling.date.start'
    _description = 'Scheduling Date Start'

    first_date_start = fields.Datetime(string='First Date Start', require=True)

    def scheduling(self):
        result = self.env['mrp.production'].search([])
        return result.button_scheduling(first_date_start=self.first_date_start)
