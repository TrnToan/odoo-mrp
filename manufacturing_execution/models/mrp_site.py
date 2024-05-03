# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import api, fields, models


class MrpSite(models.Model):
    _name = 'mrp.site'
    _description = 'Site'

    name = fields.Char(string='Site Name', required=True)
    area_ids = fields.One2many('mrp.area', 'site_id', string='Areas')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the site must be unique!')
    ]
