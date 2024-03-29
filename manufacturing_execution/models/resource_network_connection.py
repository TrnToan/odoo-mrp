# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import api, fields, models, tools


class ResourceNetworkConnection(models.Model):
    _name = 'resource.network.connection'
    _description = 'Resource Network Connection'

    from_resource_id = fields.Char(string="From Resource", required=True)
    to_resource_id = fields.Char(string="To Resource", required=True)
    name = fields.Char(string="Name", required=True)
    connection_type = fields.Char(string="Connection Type")

    def init(self):
        super(ResourceNetworkConnection, self).init()
        tools.create_index(self._cr, 'resource_network_connection_index', self._table,
                           ['from_resource_id', 'to_resource_id'])
