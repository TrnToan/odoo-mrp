# -*- coding: utf-8 -*-
import datetime

# noinspection PyUnresolvedReferences
from odoo import api, fields, models
from datetime import datetime, timedelta

import pytz
import plotly.express as px
import plotly
import pandas as pd


# Update dữ liệu lên Work Orders, bổ sung Gantt chart. Operation --> Work Orders
class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    no_priority_wo = fields.Integer(string='No.', related='production_id.no_priority_mo', store=True)
    get_mold_in_use = fields.Char(string="Mold", compute='_get_mold_in_use')
    lateness = fields.Integer(string="Lateness", related="production_id.lateness", store=True)
    get_product_id = fields.Char(string="Product ID", related='production_id.product_id.default_code', store=True)
    get_new_delivery_date = fields.Date(string='New Delivery Date', related='production_id.new_delivery_date',
                                        store=True)
    get_customer = fields.Char(string='Customer', store=True, related='production_id.get_customer')
    get_date_deadline = fields.Date(string='Date Deadline', store=True, related='production_id.new_date_deadline')
    get_quantity = fields.Float(string='Quantity', store=True, related='production_id.product_qty')
    output = fields.Float(string='Output', compute='_compute_output_from_records',
                          help="The number of products produced that meets the standard", store=True)
    scrap = fields.Float(string='Scrap', compute='_compute_scrap_from_records',
                         help="The number of products that are not up to standard", store=True)
    raw_output = fields.Float(string='Raw Output', compute='_compute_raw_output',
                              help="The total number of products produced")
    production_records = fields.One2many('mrp.production.record', 'workorder_id', string='Production Records')
    associated_equipments = fields.Char(string='Associated Equipments', compute='_get_associated_equipments',
                                        store=True)
    # OEE calculation
    availability = fields.Float(string='Availability', compute='_compute_availability', store=True)
    performance = fields.Float(string='Performance', compute='_compute_performance', store=True)
    quality = fields.Float(string='Quality', compute='_compute_quality', store=True)
    oee = fields.Float(string='OEE', compute='_compute_oee', store=True)

    def button_set_finished_to_ready(self):
        for rec in self:
            if rec.state == "done":
                rec.state = "ready"

    @api.depends('product_id')
    def _get_mold_in_use(self):
        for rec in self:
            mold = rec.env['resource.network.connection'].search([('from_resource_id', '=', rec.product_id.name),
                                                                  ('connection_type', '=', 'product_mold')], limit=1)
            if mold:
                rec.get_required_mold = mold.to_resource_id

    @api.depends('production_records')
    def _compute_output_from_records(self):
        for rec in self:
            rec.output = sum(record.output for record in rec.production_records)

    @api.depends('production_records')
    def _compute_scrap_from_records(self):
        for rec in self:
            rec.scrap = sum(record.scrap for record in rec.production_records)

    @api.depends('output', 'scrap')
    def _compute_raw_output(self):
        for rec in self:
            rec.raw_output = rec.output + rec.scrap

    @api.depends('production_records')
    def _compute_availability(self):
        """Thoi gian chay may ra san pham / Thoi gian du kien chay may"""
        for rec in self:
            if rec.production_records:
                runtime = sum((record.cycle_end_time - record.cycle_start_time).total_seconds()
                              for record in rec.production_records)
                wo_time = (datetime.utcnow() + timedelta(hours=7) - rec.date_start).total_seconds()
                rec.availability = runtime / wo_time

    @api.depends('production_records')
    def _compute_performance(self):
        """Tong san pham san xuat duoc / (Thoi gian chay may thuc te / Thoi gian chuan cua 1 san pham)"""
        for rec in self:
            if rec.production_records:
                total_injection_time = sum(record.injection_time for record in rec.production_records)
                total_injection_cycle = sum((record.cycle_end_time - record.cycle_start_time).total_seconds()
                                            for record in rec.production_records)
                rec.performance = total_injection_time / total_injection_cycle

    @api.depends('production_records')
    def _compute_quality(self):
        for rec in self:
            if rec.production_records:
                rec.quality = rec.output / (rec.output + rec.scrap)

    @api.depends('availability', 'performance', 'quality')
    def _compute_oee(self):
        for rec in self:
            rec.oee = rec.availability * rec.performance * rec.quality

    @api.depends('workcenter_id')
    def _get_associated_equipments(self):
        for rec in self:
            mold = rec.env['resource.network.connection'].search([('from_resource_id', '=', rec.product_id.name),
                                                                  ('connection_type', '=', 'product_mold')], limit=1)
            if mold:
                rec.associated_equipments = rec.workcenter_id.name + ',' + mold.to_resource_id

    @api.model
    def update_data(self):
        get_workorder = self.env['mrp.workorder'].search([])
        for workorder in get_workorder:
            super(MrpWorkorder, workorder)._onchange_expected_duration()
        return True

    @api.constrains('workcenter_id')
    def _check_workcenter_id(self):
        for rec in self:
            valid_workcenter_ids = rec.operation_id.alternative_workcenters.split(',')
            valid_workcenter_ids.append(rec.workcenter_id.code)
            if rec.workcenter_id.name not in valid_workcenter_ids:
                raise Exception('Invalid workcenter for this operation')

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
