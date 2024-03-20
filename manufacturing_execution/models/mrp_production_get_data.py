# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import fields, models

import datetime
import pytz


#  lấy dữ liệu từ ‘mrp.production’ : các list của ‘name’, ‘priority’,
# ‘weight’, ‘release_date’, ‘due_date’, ‘mold’, ‘price’, ‘quantity’ và ‘duration_expected’
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def clear_all(self):
        """
        Clears the no_priority_mo of all MOs.
        """
        get_all = self.env['mrp.production'].search([])
        for rec in get_all:
            rec.no_priority_mo = 0

    def get_mo_no(self):
        mo_no = []
        for rec in self:
            if (rec.state == 'draft') or (rec.state == 'confirmed') or (rec.state == 'progress'):
                mo_no.append(rec.no_priority_mo)
        return mo_no

    def get_mo_name(self):
        mo_name = []
        for rec in self:
            if (rec.state == 'draft') or (rec.state == 'confirmed') or (rec.state == 'progress'):
                mo_name.append(rec.name)
        return mo_name

    def get_mo_weight(self):
        mo_weight = []
        for rec in self:
            if (rec.state == 'draft') or (rec.state == 'confirmed') or (rec.state == 'progress'):
                mo_weight.append(rec.weight_so)
        return mo_weight

    def get_mo_release_date(self, first_date_start):
        mo_release_date = []
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        date_start = pytz.utc.localize(first_date_start).astimezone(user_tz)
        for rec in self:
            if (rec.state == 'draft') or (rec.state == 'confirmed') or (rec.state == 'progress'):
                if rec.release_date:
                    release_date = pytz.utc.localize(rec.release_date).astimezone(user_tz)
                    release_date_day = (release_date - date_start).days
                else:
                    release_date_day = 0
                mo_release_date.append(release_date_day * 24 * 60)  # Chuyển sang phút
        return mo_release_date

    # Được tính bằng thời gian hạn sản xuất trừ cho thời gian bắt đầu (First Date Start)
    def get_mo_due_date(self, first_date_start):
        mo_due_date = []
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        date_start = pytz.utc.localize(first_date_start).astimezone(user_tz)
        for rec in self:
            if (rec.state == 'draft') or (rec.state == 'confirmed') or (rec.state == 'progress'):
                deadline = pytz.utc.localize(rec.date_deadline_manufacturing).astimezone(user_tz)
                due_date = (deadline - date_start).days
                mo_due_date.append(due_date * 24 * 60)   # Chuyển sang phút
        return mo_due_date

    def get_mo_mold(self):
        pass

    def get_mo_price(self):
        mo_price = []
        for rec in self:
            if (rec.state == 'draft') or (rec.state == 'confirmed') or (rec.state == 'progress'):
                mo_price.append(rec.get_list_price)
        return mo_price

    def get_mo_quantity(self):
        mo_quantity = []
        for rec in self:
            if (rec.state == 'draft') or (rec.state == 'confirmed') or (rec.state == 'progress'):
                mo_quantity.append(rec.product_qty)
        return mo_quantity

    def get_mo_duration_expected(self):
        mo_duration_expected = []
        for rec in self:
            if (rec.state == 'draft') or (rec.state == 'confirmed') or (rec.state == 'progress'):
                mo_duration_expected.append(rec.production_duration_expected)
        return mo_duration_expected
