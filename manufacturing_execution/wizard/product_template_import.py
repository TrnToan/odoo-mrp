# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences

from odoo import api, fields, models, exceptions
import xlrd
import tempfile
import binascii


class ProductTemplateImport(models.TransientModel):
    _name = 'product.template.import'
    _description = 'Product Template Import'

    import_file = fields.Binary(string="Import File", required=True)
    file_name = fields.Char(string="File Name")

    def button_import_product_tmpl_xlxs(self):
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

        first_row = []  # The row where we stock the name of the column
        for col in range(sheet.ncols):
            first_row.append(sheet.cell_value(0, col))

        import_lines = []
        for row in range(1, sheet.nrows):
            record = {}
            for col in range(sheet.ncols):
                record[first_row[col]] = sheet.cell_value(row, col)
            import_lines.append(record)

        product_tmpl_ids = []
        for line in import_lines:
            if not self.check_mold_existence(line['Mold']):
                raise exceptions.UserError("Mold " + line['Mold'] + " does not exist")

            categ_id = self.env['product.category'].search([('name', '=', line['Product Category'])], limit=1).id
            route_ids = []
            for rec in line['Routes'].split(','):
                route_id = self.env['stock.location.route'].search([('name', '=', rec)], limit=1).id
                route_ids.append(route_id)
            product_tmpl_ids.append(self.env['product.template'].create({
                'name': line['Name'],
                'default_code': line['Internal Reference'],
                'list_price': line['Sales Price'],
                'categ_id': categ_id,
                'type': line['Product Type'],
                'purchase_ok': line['Can be Purchased'],
                'sale_ok': line['Can be Sold'],
                'route_ids': [(6, 0, route_ids)],
                'description': line['Description'],
            }))
            self.env['resource.network.connection'].create({
                'from_resource_id': line['Name'],
                'to_resource_id': line['Mold'],
                'name': line['Name'] + ' is molded from ' + line['Mold'],
            })

        view_id = self.env.ref('manufacturing_execution.product_template_product_tree_inherited').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Product Template',
            'view_mode': 'tree',
            'res_model': 'product.template',
            'view_id': view_id,
            'domain': [('id', 'in', [product_tmpl.id for product_tmpl in product_tmpl_ids])],
        }
        return action

    def check_mold_existence(self, mold):
        if not self.env['equipment.equipment'].search([('name', '=', mold)]):
            return False
        return True
