# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models

import pandas as pd
import datetime
import pytz


# cập nhật dữ liệu lên Manufacturing Orders. Operation --> Manufacturing Orders
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    date_deadline_manufacturing = fields.Datetime(string='Deadline Manufacturing', compute='_cal_deadline_manufacturing')
    weight_so = fields.Float(string='Weight', compute='_find_weight_customer', store=True)
    no_priority_mo = fields.Integer(string='No.', default=0, store=True, help="The priority of the MO")
    get_category_id = fields.Many2one('product.category', 'Category', related='product_id.categ_id', store=True)
    get_list_price = fields.Float(string='Price', related='product_id.list_price')
    get_mold_in_use = fields.Char(string="Mold in Use", compute='_get_mold_in_use')
    release_date = fields.Datetime(string='Release Date',
                                   help="Date on which all the material needed for poduction is ready")
    lateness = fields.Integer(string="Lateness", store=True, compute='_cal_lateness')
    production_duration_expected = fields.Float(string='Expected Duration', compute='_cal_duration_expected')
    new_delivery_date = fields.Date(string='New Delivery Date', store=True, compute='_cal_new_delivery_date')
    get_customer = fields.Char(string='Customer', store=True, compute='_find_customer')
    new_date_deadline = fields.Date(string='Date Deadline', store=True, compute='_cal_date_deadline')


    @api.depends('product_id')
    def _get_mold_in_use(self):
        for rec in self:
            mold = rec.env['resource.network.connection'].search([('from_resource_id', '=', rec.name)], limit=1)
            if mold:
                rec.get_required_mold = mold.to_resource_id

    @api.depends('date_deadline')
    def _cal_deadline_manufacturing(self):
        for rec in self:
            if rec.date_deadline:
                rec.date_deadline_manufacturing = rec.date_deadline - datetime.timedelta(days=3)

    @api.depends('workorder_ids')
    def _cal_duration_expected(self):
        """
        1 MO only contains 1 WO
        """
        for rec in self:
            rec.production_duration_expected = rec.workorder_ids.duration_expected

    @api.depends('date_planned_finished')
    def _cal_new_delivery_date(self):
        for rec in self:
            if rec.date_planned_finished:
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                date_planned_finished = pytz.utc.localize(rec.date_planned_finished).astimezone(user_tz)
                rec.new_delivery_date = date_planned_finished.date() + datetime.timedelta(days=3)

    @api.depends('date_deadline')
    def _cal_date_deadline(self):
        """
        Localize date_deadline and convert to date
        """
        for rec in self:
            if rec.date_deadline:
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                date_deadline = pytz.utc.localize(rec.date_deadline).astimezone(user_tz)
                rec.new_date_deadline = date_deadline.date()

    @api.depends('new_delivery_date', 'date_deadline')
    def _cal_lateness(self):
        for rec in self:
            if rec.new_delivery_date:
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                date_deadline = pytz.utc.localize(rec.date_deadline).astimezone(user_tz)
                lateness = rec.new_delivery_date - date_deadline.date()
                rec.lateness = lateness.days
            else:
                rec.lateness = 0

    @api.depends('origin')
    def _find_customer(self):
        for rec in self:
            if rec.origin:
                get_so = rec.env['sale.order'].search([('name', '=', rec.origin)])
                rec.get_customer = get_so.partner_id.name

    @api.depends('get_customer')
    def _find_weight_customer(self):
        for rec in self:
            if rec.get_customer:
                get_res_partner = rec.env['res.partner'].search([('name', '=', rec.get_customer)])
                rec.weight_so = get_res_partner.weight

    def input_data(self, first_date_start):
        mo_name = self.get_mo_name()
        mo_weight = self.get_mo_weight()
        mo_release_date = self.get_mo_release_date(first_date_start)
        mo_due_date = self.get_mo_due_date(first_date_start)
        mo_mold = self.get_mo_mold()
        mo_duration_expected = self.get_mo_duration_expected()
        all_info = {
            'name': mo_name,
            'wj': mo_weight,
            'rj': mo_release_date,
            'dj': mo_due_date,
            'mold': mo_mold,
            'pj': mo_duration_expected
        }
        instance_dict = pd.DataFrame(all_info)
        print(instance_dict)
        instance_dict = instance_dict.sort_values(by=['dj', 'name'], ascending=True)
        print("After sort")
        print(instance_dict)
        index = pd.Series([i for i in range(1, len(mo_name) + 1)])
        instance_dict = instance_dict.set_index([index], 'name')
        print("After set index")
        print(instance_dict)
        instance_dict = instance_dict.to_dict('index')
        self.dictionary_display(instance_dict)
        return instance_dict

    def mo_no_priority(self, first_date_start):
        instance_dict = self.input_data(first_date_start)
        order_name = []
        order_weight = []
        order_release_date = []
        order_due_date = []
        order_duration_expected = []
        for job in range(1, len(instance_dict) + 1):
            order_name.append(instance_dict[job]['name'])
            order_weight.append(instance_dict[job]['wj'])
            order_release_date.append(instance_dict[job]['rj'])
            order_due_date.append(instance_dict[job]['dj'])
            order_duration_expected.append(instance_dict[job]['pj'])
        order_all_info = {
            'name': order_name,
            'wj': order_weight,
            'rj': order_release_date,
            'dj': order_due_date,
            'pj': order_duration_expected
        }
        order_instance_dict = (pd.DataFrame(order_all_info, index=[i for i in range(1, len(order_name) + 1)])
                               .to_dict('index'))
        self.dictionary_display(instance_dict)

        # Đánh stt theo ngẫu nhiên. Phải dùng Tabu search để tối ưu
        i = 1
        for job in range(0, len(order_instance_dict)):
            for rec in self:
                if rec.name == order_instance_dict[job+1]['name']:
                    # gán stt thực hiện vào từng đơn MO: SL MO - stt MO + 1
                    rec.no_priority_mo = len(order_instance_dict) - i + 1
            i += 1

    def button_set_done_to_cancel(self):
        for rec in self:
            if rec.state == "done":
                rec.state = "cancel"

    def button_scheduling(self, first_date_start):
        self.button_unplan()
        self.clear_all()
        self.mo_no_priority(first_date_start)

    def button_planning(self, first_date_start):
        print("Planning execution")
        self.button_unplan()
        self.change_date_planned_start(first_date_start)

    def dictionary_display(self, instance_dict):
        print("After to dict")
        for key, value in instance_dict.items():
            print(f'{key}: {value}')
