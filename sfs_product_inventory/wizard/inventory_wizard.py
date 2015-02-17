# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

from datetime import datetime
import base64
import time
from tools.translate import _

class inventory_update_wizard(osv.osv_memory):
    _name = 'inventory.update.wizard'
    _description = 'Wizard to update inventory from txt file'
    _columns = {
                'inv_file': fields.binary('File'),
                'location_id': fields.many2one('stock.location', 'Location'),
                'update_summery': fields.text('Updation Log', readonly=True)
                }
    
    def update_inv(self, cr, uid, ids, context=None):
        updated_product_referances = []
        failed_updation = []
        inventory_pool = self.pool.get('stock.inventory')
        product_pool = self.pool.get('product.product')
        inventory_line_pool = self.pool.get('stock.inventory.line')
        mod_obj = self.pool.get('ir.model.data')
        inv_id = False
        data = self.read(cr, uid, ids, context=context)[0]
        location_id = data['location_id'][0]
        file = data['inv_file']
        file_data = base64.decodestring(file)
        data_list = file_data.split('\n')
        if data_list and not inv_id:
            date = (datetime.now()).strftime('%d-%m-%y %H:%M:%S')
            vals = {
                    'name': 'Inventory Update ' + str(date),
                    }
            inv_id = inventory_pool.create(cr, uid, vals, context=context)
        for data in data_list:
            line_data = {}
            line_data_list = data.split(',')
            if len(line_data_list) > 2:
                product_code = line_data_list[1]
                product_qty = line_data_list[2]
                product_ids = product_pool.search(cr, uid, [('default_code', '=', product_code)], context=context)
                if product_ids:
                    updated_product_referances.append(product_code)
                else:
                    failed_updation.append(product_code)
                if product_ids:
                    product_obj = product_pool.browse(cr, uid, product_ids[0], context=context)
                    line_data = {
                                 'location_id': location_id,
                                 'product_id': product_ids[0],
                                 'product_qty': product_qty,
                                 'product_uom': product_obj.uom_id.id,
                                 'inventory_id': inv_id
                                 }
                    inventory_line_pool.create(cr, uid, line_data, context=context)
        inventory_pool.action_confirm(cr, uid, [inv_id], context=context)
        if not failed_updation:
            message = "Products with following Reference are updated:\n%s"%('\n'.join(updated_product_referances))
        else:
            message = """Products with following Reference are updated:\n%s
----------------------------------------------------------------
Failed Updations: \n%s
"""%(('\n'.join(updated_product_referances)),('\n'.join(failed_updation)))
        model_data_ids = mod_obj.search(cr, uid, [('model','=','ir.ui.view'),
                                                  ('name','=','inventory_update_wizard_summery')], 
                                        context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        self.write(cr, uid, ids, {'update_summery': message}, context=context)
        return {
                'name': _('Inventory Update Summary'),
                'view_type': 'form',
                'context': context,
                'view_mode': 'tree,form',
                'res_model': 'inventory.update.wizard',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'nodestroy': True,
                'res_id': ids and ids[0] or False,
                }
    
inventory_update_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
