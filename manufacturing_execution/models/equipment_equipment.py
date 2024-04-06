# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import api, fields, models


class Equipment(models.Model):
    _name = "equipment.equipment"
    _description = "Equipment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    code = fields.Char(string="Equipment Code", required=True)
    name = fields.Char(string="Equipment Name", required=True)
    description = fields.Text(string="Description")
    total_quantity = fields.Integer(string="Total Quantity", required=True, help="Total quantity of the equipments")
    available_quantity = fields.Integer(string="Available Quantity", compute='_compute_available_quantity',
                                        help="Number of equipments being available for use")
    workcenter_id = fields.Many2one('mrp.workcenter', string="Work Center")
    area_id = fields.Many2one('mrp.area', string="Area")
    site_id = fields.Many2one('mrp.site', string="Site")
    equipment_type_id = fields.Many2one('equipment.type', string="Equipment Type")
    equipment_property_ids = fields.One2many('equipment.property', 'equipment_id', string="Equipment Property")

    @api.depends('total_quantity')
    def _compute_available_quantity(self):
        equipments_in_use = []
        progress_workorders = self.env['mrp.workorder'].search([('state', '=', 'progress')])
        for workorder in progress_workorders:
            equipments_in_use = (equipments_in_use +
                                 (workorder.associated_equipments.split(',') if workorder.associated_equipments else []))

        for rec in self:
            if equipments_in_use:
                rec.available_quantity = rec.total_quantity - equipments_in_use.count(rec.name)
            else:
                rec.available_quantity = rec.total_quantity
