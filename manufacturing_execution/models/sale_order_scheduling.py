# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models

from pprint import pprint
import pytz


# Thêm các fields vào trong models ‘sale.order’, lập trình các nút nhấn trên giao diện Sale Quotations
class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date = fields.Datetime(tracking=True)
    new_commitment_date = fields.Date(string='New Commitment Date', store=True, compute='_cal_commitment_date')
    sum_quantity = fields.Float(string='Quantity', store=True, compute='_cal_sum_quantity')

    @api.depends('commitment_date')
    def _cal_commitment_date(self):
        for rec in self:
            if rec.commitment_date:
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                commitment_date = pytz.utc.localize(rec.commitment_date).astimezone(user_tz)
                rec.new_commitment_date = commitment_date.date()
            else:
                rec.new_commitment_date = None

    @api.depends('order_line.product_uom_qty')
    def _cal_sum_quantity(self):
        for rec in self:
            rec.sum_quantity = sum(rec.order_line.mapped('product_uom_qty'))

    def button_set_to_quotation(self):
        for rec in self:
            if rec.state == "cancel":
                rec.action_draft()

    def button_confirm(self):
        for rec in self:
            if rec.state == "draft":
                rec.action_confirm()

    def button_cancel(self):
        for rec in self:
            if rec.state == "draft":
                rec.action_cancel()
            if rec.state == "sale":
                rec.action_cancel()
                mo = rec.env['mrp.production'].search([['origin', '=', rec.name]])
                for val in mo:
                    val.action_cancel()

