# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2011 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    conatct@zbeanztech.com
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

class stock_partial_picking(osv.osv_memory):
    _inherit = 'stock.partial.picking'

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        pick_obj = self.pool.get('stock.picking')
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        for pick in pick_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            has_product_cost = (pick.type == 'in' and pick.purchase_id)
            for m in pick.move_lines:
                if m.state in ('done','cancel') :
                    continue
                if has_product_cost and m.product_id.cost_method == 'average' and m.purchase_line_id:
                    # We use the original PO unit purchase price as the basis for the cost, expressed
                    # in the currency of the PO (i.e the PO's pricelist currency)
                    list_index = 0
                    for item in res['product_moves_in']:
                        if item['move_id'] == m.id:
                            res['product_moves_in'][list_index]['cost'] = m.purchase_line_id.total_unit_price_exp
                            res['product_moves_in'][list_index]['currency'] = m.company_id.currency_id.id
                        list_index += 1
        return res
stock_partial_picking()