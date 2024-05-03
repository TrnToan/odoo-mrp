# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    equipment_ids = fields.One2many('equipment.equipment', 'workcenter_id', string="Equipments")
    area_id = fields.Many2one('mrp.area', string='Related Area')
    site_id = fields.Many2one(related='area_id.site_id', string='Related Site')
    enterprise_id = fields.Many2one(string='Enterprise', related='area_id.site_id.company_id')
    # alternative_workcenter_ids = fields.Many2many('mrp.workcenter', compute='_get_alternative_workcenters')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Workcenter name must be unique'),
        ('code_uniq', 'unique(code)', 'Workcenter code must be unique')
    ]
