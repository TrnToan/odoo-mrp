# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


class MrpArea(models.Model):
    _name = 'mrp.area'
    _description = 'Area'

    name = fields.Char(string='Area Name', required=True)
    site_id = fields.Many2one('mrp.site', string='Site')
    workcenter_ids = fields.One2many('mrp.workcenter', 'area_id', string='Workcenters')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the area must be unique!')
    ]
