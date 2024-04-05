# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PlanningDateStart(models.TransientModel):
    _name = 'planning.date.start'
    _description = 'Planning Date Start'

    first_date_start = fields.Datetime(string='First Date Start', require=True)

    def planning(self):
        selected_ids = self.env.context.get('active_ids', [])
        result = self.env['mrp.production'].browse(selected_ids)
        return result.button_planning(first_date_start=self.first_date_start)
