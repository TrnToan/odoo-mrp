# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import api, fields, models, exceptions
import xlrd
import re
import tempfile
import binascii


class ProductBomImport(models.TransientModel):
    _name = 'product.bom.import'
    _description = 'Product BOM Import'

    import_file = fields.Binary(string="Import File", required=True)

    def button_import_product_bom_xlxs(self):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.import_file))
            fp.seek(0)
            fp.close()
        except:
            raise exceptions.UserError("Invalid File !!!")

        workbook = xlrd.open_workbook(fp.name, on_demand=True)
        sheet = workbook.sheet_by_index(0)

        if sheet.ncols == 0:
            return

        first_row = []
        for col in range(sheet.ncols):
            first_row.append(sheet.cell_value(0, col))

        import_lines = []
        for row in range(1, sheet.nrows):
            record = {}
            for col in range(sheet.ncols):
                record[first_row[col]] = sheet.cell_value(row, col)
            import_lines.append(record)

        product_bom_ids = []
        for line in import_lines:
            product_tmpl_id = self.env['product.template'].search([('default_code', '=', line['Reference'])], limit=1).id
            product_code = self.get_code_from_component(line['BoM Lines/Component'])
            product_id = self.env['product.product'].search([('default_code', '=', product_code)], limit=1).id
            product_uom_id = self.env['uom.uom'].search([('name', '=', line['Unit of Measure'])], limit=1).id
            workcenter_id = self.env['mrp.workcenter'].search([('name', '=', line['Operations/Work Center'])], limit=1).id
            product_bom_ids.append(self.env['mrp.bom'].create({
                'product_tmpl_id': product_tmpl_id,
                'code': line['Reference'],
                'type': line['BoM Type'],
                'bom_line_ids': [(0, 0, {
                    'product_id': product_id,
                    'product_qty': line['Quantity'],
                    'product_uom_id': product_uom_id,
                })],
                'operation_ids': [(0, 0, {
                    'name': line['Operations/Operation'],
                    'workcenter_id': workcenter_id,
                    'alternative_workcenters': line['Operations/Alternative Workcenters'],
                    'time_mode': line['Operations/Duration Computation'],
                    'time_cycle_manual': line['Operations/Manual Duration'],
                })]
            }))

            product_name = self.get_name_from_component(line['BoM Lines/Component'])
            self.env['resource.network.connection'].create({
                'from_resource_id': product_name,
                'to_resource_id': line['Operations/Work Center'],
                'name': product_name + ' is produced at workcenter ' + line['Operations/Work Center'],
                'connection_type': "product_workcenter"
            })

        view_id = self.env.ref('mrp.mrp_bom_tree_view').id
        action = {
            'name': 'BOM',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'view_mode': 'tree',
            'view_id': view_id,
            'target': 'current',
            'domain': [('id', 'in', [product_bom.id for product_bom in product_bom_ids])],
        }
        return action

    # A component is a string that contains the product default code and its name. Format: [code] name
    @staticmethod
    def get_code_from_component(component):
        """Extracts the product code from the BoM Lines/component."""
        result = re.search('\[(.*?)\]', component)
        if result:
            return result.group(1)
        return None

    @staticmethod
    def get_name_from_component(component):
        """Extracts the product name from the BoM Lines/component."""
        return re.sub('\[.*?\]\s', '', component)
