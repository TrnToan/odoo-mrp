# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


class EquipmentProperty(models.Model):
    _name = "equipment.property"
    _description = "Equipment Property"

    equipment_id = fields.Many2one('equipment.equipment', string='Equipment')
    property_id = fields.Char(string="Property Name")
    description = fields.Char(string="Description")
    property_value_string = fields.Char(string="Property Value")
    property_value_type = fields.Selection([
        ('boolean', 'Boolean'),
        ('integer', 'Integer'),
        ('decimal', 'Decimal'),
        ('float', 'Float'),
        ('string', 'String')
    ], default='boolean')
    property_value_unit = fields.Char(string="Property's Value Unit")
