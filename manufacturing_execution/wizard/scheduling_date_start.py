# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SchedulingDateStart(models.TransientModel):
    _name = 'scheduling.date.start'
    _description = 'Scheduling Date Start'

    first_date_start = fields.Datetime(string='First Date Start', require=True)

    def scheduling_planning(self):
        selected_ids = self.env.context.get('active_ids', [])
        result = self.env['mrp.production'].browse(selected_ids)
        return result.button_scheduling_planning(first_date_start=self.first_date_start)
