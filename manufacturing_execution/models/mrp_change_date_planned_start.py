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
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        if date:
            get_local_date = pytz.utc.localize(date).astimezone(user_tz)
            get_local_date = get_local_date.strftime("%Y-%m-%d %H:%M:%S")
            get_local_date = datetime.datetime.strptime(get_local_date, "%Y-%m-%d %H:%M:%S")
        else:
            get_local_date = 0
        return get_local_date

    def data_date_planned_start(self):
        print("data_date_planned_start")
        mo_no = []
        mo_name = []
        mo_bom = []
        mo_workcenter = []
        mo_mold = []
        mo_release_date = []
        mo_date_start = []
        mo_date_finish = []
        mo_deadline_manufacturing = []
        mo_duration_expected = []
        for rec in self:
            mo_no.append(rec.no_priority_mo)
            mo_name.append(rec.name)
            mo_bom.append(rec.bom_id.code)
            routing = rec.env['mrp.routing.workcenter'].search([('bom_id.code', '=', rec.bom_id.code)])
            mo_workcenter.append(routing.workcenter_id.name)
            mo_mold.append(rec.get_mold)
            mo_release_date.append(self.get_date(rec.release_date))
            mo_date_start.append(self.get_date(rec.date_planned_start))
            mo_date_finish.append(self.get_date(rec.date_planned_finished))
            mo_deadline_manufacturing.append(self.get_date(rec.date_deadline_manufacturing))
            mo_duration_expected.append(rec.production_duration_expected)
        all_info = {'no': mo_no,
                    'name': mo_name,
                    'bom': mo_bom,
                    'workcenter': mo_workcenter,
                    'mold': mo_mold,
                    'release_date': mo_release_date,
                    'date_start': mo_date_start,
                    'date_finish': mo_date_finish,
                    'deadline_manufacturing': mo_deadline_manufacturing,
                    'duration_expected': mo_duration_expected}
        instance_dict = pd.DataFrame(all_info)
        instance_dict = instance_dict.sort_values(by='no', ascending=False)
        index = pd.Series([i for i in range(1, len(mo_name) + 1)])
        instance_dict = instance_dict.set_index([index], 'name')
        instance_dict = instance_dict.to_dict('index')
        return instance_dict

    def first_date_planned_start(self, first_date_start):
        date_planned_start = self.get_date(first_date_start).strftime("%Y-%m-%d %H:%M:%S")
        first_date_planned_start = datetime.datetime.strptime(date_planned_start, "%Y-%m-%d %H:%M:%S")
        return first_date_planned_start

    def change_format_date(self, date):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        local_date_planned_start = user_tz.localize(date)
        utc_date_planned_start = local_date_planned_start.astimezone(pytz.utc)
        str_date_planned_start = utc_date_planned_start.strftime("%Y-%m-%d %H:%M:%S")
        change_date_planned_start = datetime.datetime.strptime(str_date_planned_start, "%Y-%m-%d %H:%M:%S")
        return change_date_planned_start

    def find_date_planned_start(self, instance_dict, job, first_date_start):
        find = []
        for i in range(1, job + 1):
            if instance_dict[i]['workcenter'] == instance_dict[job]['workcenter']:
                find.append(instance_dict[i])
        if len(find) == 1:
            first_date_planned_start = self.first_date_planned_start(first_date_start)
            if find[-1]['release_date'] != 0:
                if find[-1]['release_date'] > first_date_planned_start:
                    date_start = find[-1]['release_date']
                else:
                    date_start = first_date_planned_start
            else:
                date_start = first_date_planned_start
        else:
            next_date_start = find[-2]['date_finish']
            if find[-1]['mold'] != find[-2]['mold']:
                next_date_start = find[-2]['date_finish'] + datetime.timedelta(hours=3)
            if find[-1]['release_date'] != 0:
                if find[-1]['release_date'] > next_date_start:
                    date_start = find[-1]['release_date']
                else:
                    date_start = next_date_start
            else:
                date_start = next_date_start
        return date_start

    def change_workcenter(self, name, new_workcenter):
        workcenter = self.env['mrp.workcenter'].search([('name', '=', new_workcenter)])
        get_work_orders = self.env['mrp.workorder'].search([])
        for rec in get_work_orders:
            if rec.production_id.name == name:
                rec.workcenter_id = workcenter

    def submit_date_start(self, rec, instance_dict, job, first_date_start):
        self.change_workcenter(name=rec.name, new_workcenter=instance_dict[job]['workcenter'])
        date_start = self.find_date_planned_start(instance_dict=instance_dict,
                                                  job=job,
                                                  first_date_start=first_date_start)
        instance_dict[job]['date_start'] = date_start
        rec.date_planned_start = self.change_format_date(date_start)
        rec.button_plan()
        instance_dict[job]['date_finish'] = self.get_date(rec.date_planned_finished)

    def change_date_planned_start(self, first_date_start):
        instance_dict = self.data_date_planned_start()
        n_jobs = len(instance_dict)
        index = list(range(1, n_jobs + 1))

        for job in index:
            for rec in self:
                if rec.state == 'confirmed' and rec.name == instance_dict[job]['name']:
                    self.submit_date_start(rec, instance_dict, job, first_date_start)

