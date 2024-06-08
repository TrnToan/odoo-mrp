# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import fields, models

import pandas as pd
import datetime
import pytz
from pprint import pprint


# Tự động lên lịch cho từng lệnh sản xuất, đưa ra thời gian bắt đầu và thời gian kết thúc của từng đơn sản xuất
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def get_date(self, date):
        """
        Đọc first_date_start theo local time zone
        """
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        if date:
            get_local_date = pytz.utc.localize(date).astimezone(user_tz)
            get_local_date = get_local_date.strftime("%Y-%m-%d %H:%M:%S")
            get_local_date = datetime.datetime.strptime(get_local_date, "%Y-%m-%d %H:%M:%S")
        else:
            get_local_date = 0
        return get_local_date

    def change_format_date(self, date):
        """
        Chuyển format date sang local datetime
        """
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        local_date_planned_start = user_tz.localize(date)
        utc_date_planned_start = local_date_planned_start.astimezone(pytz.utc)
        str_date_planned_start = utc_date_planned_start.strftime("%Y-%m-%d %H:%M:%S")
        change_date_planned_start = datetime.datetime.strptime(str_date_planned_start, "%Y-%m-%d %H:%M:%S")
        return change_date_planned_start

    def first_date_planned_start(self, first_date_start):
        """
        Gán ngày bắt đầu là first_date_start (first_date_start là thời điểm bắt đầu làm việc của máy)
        Trả về kiêu datetime
        """
        date_planned_start = self.get_date(first_date_start).strftime("%Y-%m-%d %H:%M:%S")
        first_date_planned_start = datetime.datetime.strptime(date_planned_start, "%Y-%m-%d %H:%M:%S")
        return first_date_planned_start

    def change_workcenter(self, name, new_workcenter):
        """
        Tìm kiếm trong model workcenter máy ép gán máy ép vào workorder
        workcenter không được thể hiện trong MO mà là trong WO
        """
        workcenter = self.env['mrp.workcenter'].search([('name', '=', new_workcenter)])
        get_work_orders = self.env['mrp.workorder'].search([])
        for rec in get_work_orders:
            if rec.production_id.name == name:
                rec.workcenter_id = workcenter
