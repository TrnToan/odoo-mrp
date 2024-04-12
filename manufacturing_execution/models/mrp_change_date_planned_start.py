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

    def find_date_planned_start(self, instance_dict, job, first_date_start):
        """
        Tính toán ngày bắt đầu cho MO thứ job (job: stt)
        """
        # instance_dict chua thong tin cua cac MO duoc thuc hien boi cung mot workcenter

        # find = []
        # # tìm kiếm tất cả các MO đã được lên lịch trên máy ép của MO thứ job rồi add vào list find bên trên
        # for i in range(1, job + 1):
        #     if instance_dict[i]['workcenter'] == instance_dict[job]['workcenter']:
        #         find.append(instance_dict[i])
        #
        # # nếu MO thứ job là MO đầu tiên trên máy này thì
        # if len(find) == 1:
        #     first_date_planned_start = self.first_date_planned_start(first_date_start)
        #     if find[-1]['release_date'] != 0:
        #         if find[-1]['release_date'] > first_date_planned_start:
        #             date_start = find[-1]['release_date']
        #         else:
        #             date_start = first_date_planned_start
        #     else:
        #         date_start = first_date_planned_start
        # else:
        #     next_date_start = find[-2]['date_finish']
        #     if find[-1]['mold'] != find[-2]['mold']:
        #         # cộng thêm thời gian thay khuôn trong trường hợp khuôn của 2 đơn ko giống nhau
        #         next_date_start = find[-2]['date_finish'] + datetime.timedelta(hours=3)
        #     if find[-1]['release_date'] != 0:
        #         if find[-1]['release_date'] > next_date_start:
        #             date_start = find[-1]['release_date']
        #         else:
        #             date_start = next_date_start
        #     else:
        #         date_start = next_date_start
        # return date_start

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
