# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import api, fields, models


class EquipmentType(models.Model):
    _name = "equipment.type"
    _description = "Equipment Type"

    name = fields.Char(string="Equipment Type", required=True)
    equipment_ids = fields.One2many('equipment.equipment', 'equipment_type_id', string="Equipments")
