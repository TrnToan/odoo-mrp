# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PlanningDateStart(models.TransientModel):
    _name = 'planning.date.start'
    _description = 'Planning Date Start'

    first_date_start = fields.Datetime(string='First Date Start', require=True)

    def planning(self):
        result = self.env['mrp.production'].search([])
        return result.button_planning(first_date_start=self.first_date_start)
