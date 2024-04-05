# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import fields, models

import datetime
import pytz


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def clear_all(self):
        """
        Clears the no_priority_mo of all MOs.
        """
        get_all = self.env['mrp.production'].search([])
        for rec in get_all:
            rec.no_priority_mo = 0

    def get_time_range(self, date, first_date_start):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        date_start = pytz.utc.localize(first_date_start).astimezone(user_tz)
        date = pytz.utc.localize(date).astimezone(user_tz)
        time_range = (date - date_start).days
        return time_range * 24 * 60 # Chuyển sang phút
