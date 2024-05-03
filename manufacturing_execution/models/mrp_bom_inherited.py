from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def create(self, values):
        operations = values.get('operation_ids')
        product_tmpl_id = values.get('product_tmpl_id')
        product = self.env['product.template'].search([('id', '=', product_tmpl_id)], limit=1).name
        for operation in operations:
            mold = operation[2].get('mold')
            workcenter_id = operation[2].get('workcenter_id')
            if self.check_mold_existence(mold):
                self.env['resource.network.connection'].create({
                    'from_resource_id': product,
                    'to_resource_id': mold,
                    'connection_type': 'product_mold',
                    'connection_name': 'Product ' + product + ' is molded by ' + mold
                })

            workcenter = self.env['mrp.workcenter'].search([('id', '=', workcenter_id)], limit=1).code
            if workcenter:
                self.env['resource.network.connection'].create({
                    'from_resource_id': product,
                    'to_resource_id': workcenter,
                    'connection_type': 'product_workcenter',
                    'connection_name': 'Product ' + product + ' is produced at workcenter ' + workcenter
                })
        return super(MrpBom, self).create(values)

    def unlink(self):
        operations = self.operation_ids
        product_tmpl_id = operations['bom_id'].product_tmpl_id.id
        product = self.env['product.template'].search([('id', '=', product_tmpl_id)], limit=1).name

        for operation in operations:
            mold = operation['mold']
            workcenter = operation['workcenter_id'].code
            self.env['resource.network.connection'].search([('from_resource_id', '=', product),
                                                            ('to_resource_id', '=', mold),
                                                            ('connection_type', '=', 'product_mold')]).unlink()

            self.env['resource.network.connection'].search([('from_resource_id', '=', product),
                                                            ('to_resource_id', '=', workcenter),
                                                            ('connection_type', '=', 'product_workcenter')]).unlink()
        return super(MrpBom, self).unlink()

    def check_mold_existence(self, mold):
        existing_mold = self.env['equipment.equipment'].search([('name', '=', mold)], limit=1)
        if not existing_mold:
            return False
        return True
