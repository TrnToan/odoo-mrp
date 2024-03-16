# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models

import pytz

import plotly.express as px
import plotly
import pandas as pd


# Update dữ liệu lên Work Orders, bổ sung Gantt chart. Operation --> Work Orders
class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    no_priority_wo = fields.Integer(string='No.', related='production_id.no_priority_mo', store=True)
    get_mold = fields.Char(string="Mold", related='product_id.mold')
    lateness = fields.Integer(string="Lateness", related="production_id.lateness", store=True)
    get_product_id = fields.Char(string="Product ID", related='production_id.product_id.default_code', store=True)
    get_new_delivery_date = fields.Date(string='New Delivery Date', related='production_id.new_delivery_date',
                                        store=True)
    get_customer = fields.Char(string='Customer', store=True, related='production_id.get_customer')
    get_date_deadline = fields.Date(string='Date Deadline', store=True, related='production_id.new_date_deadline')
    get_quantity = fields.Float(string='Quantity', store=True, related='production_id.product_qty')

    def button_set_finished_to_ready(self):
        for rec in self:
            if rec.state == "done":
                rec.state = "ready"

    @api.model
    def update_data(self):
        get_workorder = self.env['mrp.workorder'].search([])
        for workorder in get_workorder:
            super(MrpWorkorder, workorder)._onchange_expected_duration()
        return True

    def change_local_time(self, time):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        time_change = pytz.utc.localize(time).astimezone(user_tz)
        return time_change

    def view_gantt(self):
        work_orders = self.env['mrp.workorder'].search([])
        lateness_so = {work_order.production_id.origin: [origin.lateness
                                                         for origin in work_orders
                                                         if
                                                         origin.production_id.origin == work_order.production_id.origin
                                                         and origin.lateness > 0]
                       for work_order in work_orders if work_order.lateness > 0 and work_order.date_planned_start}
        lateness_mo = [[work_order.production_id.product_id.default_code, work_order.lateness]
                       for work_order in work_orders
                       if work_order.lateness > 0 and work_order.date_planned_start]
        msg_lateness_so = [[key, max(value)] for (key, value) in lateness_so.items()]
        new_title = f"Số đơn hàng bán hàng trễ: {len(msg_lateness_so)}<br>Số ngày trễ tối đa: "
        for rec in msg_lateness_so:
            new_title += f"{rec[0]}-{rec[1]} | "
            if msg_lateness_so.index(rec) == 9:
                new_title += f"<br>                            "

        new_title += f"<br>Đơn sản xuất trễ: "
        for rec in lateness_mo:
            new_title += f"{rec[0]}({rec[1]}) | "
            if lateness_mo.index(rec) == 6:
                new_title += f"<br>"
        work_center = [work_order.workcenter_id.name for work_order in work_orders if work_order.date_planned_start]
        operation = [work_order.production_id.product_id.default_code for work_order in work_orders if
                     work_order.date_planned_start]
        date_start = [self.change_local_time(work_order.date_planned_start).strftime('%Y-%m-%d %H:%M') for work_order in
                      work_orders if work_order.date_planned_start]
        date_finish = [self.change_local_time(work_order.date_planned_finished).strftime('%Y-%m-%d %H:%M') for
                       work_order in work_orders if work_order.date_planned_start]
        all_info = {
            'Work Center': work_center,
            'Date Start': date_start,
            'Date Finish': date_finish,
            'Operation': operation
        }
        data = pd.DataFrame(all_info)
        fig = px.timeline(data, title=new_title, x_start=data['Date Start'], x_end=data['Date Finish'],
                          y=data['Work Center'], color=data['Operation'])
        plotly.offline.plot(fig, filename='Gantt Chart.html')
