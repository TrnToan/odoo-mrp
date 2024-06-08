# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import fields, models
import pandas as pd
import datetime
import pytz


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def get_data_groupby_workcenter(self):
        """
        Lấy dữ liệu của tất cả các MO cần lên lịch --> gom lại theo từng workcenter
        """
        mo_no = []
        mo_name = []
        mo_weight = []
        mo_bom = []
        mo_workcenter = []
        mo_mold = []
        mo_release_date = []
        mo_date_planned_start = []
        mo_date_planned_finish = []
        mo_deadline_manufacturing = []
        mo_duration_expected = []
        for rec in self:
            mo_no.append(rec.no_priority_mo)
            mo_name.append(rec.name)
            mo_weight.append(rec.weight_so)
            mo_bom.append(rec.bom_id.code)

            routing = rec.env['mrp.routing.workcenter'].search([('bom_id.code', '=', rec.bom_id.code)])
            mo_workcenter.append(routing.workcenter_id.name)

            product = rec.env['product.template'].search([('name', '=', rec.product_id.name)])
            mold = rec.env['resource.network.connection'].search([('from_resource_id', '=', product.name),
                                                                  ('connection_type', '=', 'product_mold')])
            mo_mold.append(mold)

            mo_release_date.append(self.get_date(rec.release_date))
            mo_date_planned_start.append(self.get_date(rec.date_planned_start))
            mo_date_planned_finish.append(self.get_date(rec.date_planned_finished))
            mo_deadline_manufacturing.append(self.get_date(rec.date_deadline_manufacturing))
            mo_duration_expected.append(rec.production_duration_expected)

        all_info = {'no': mo_no,
                    'name': mo_name,
                    'weight': mo_weight,
                    'bom': mo_bom,
                    'workcenter': mo_workcenter,
                    'mold': mo_mold,
                    'release_date': mo_release_date,
                    'date_start': mo_date_planned_start,
                    'date_finish': mo_date_planned_finish,
                    'deadline_manufacturing': mo_deadline_manufacturing,
                    'duration_expected': mo_duration_expected}
        df = pd.DataFrame(all_info)
        df_groupby_workcenter = df.groupby('workcenter')
        return df_groupby_workcenter

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
