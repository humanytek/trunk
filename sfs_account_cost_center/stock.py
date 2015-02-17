# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
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
from tools.translate import _

class stock_warehouse(osv.osv):
    _inherit = 'stock.warehouse'
    _columns = {
                'journal_id': fields.many2one('account.journal', 'Journals')
                }
stock_warehouse()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        warehouse_pool = self.pool.get('stock.warehouse')
        product_obj=self.pool.get('product.product')
        picking_type = move.picking_id and move.picking_id.type or 'internal'
        if picking_type == 'out':
            location = move.location_id or False
        else:
            location = move.location_dest_id or False
        location_id = location and location.id or False
        warehouse_ids = warehouse_pool.search(cr, uid, ['|', ('lot_input_id', '=', location_id),
                                                        ('lot_stock_id', '=', location_id)],
                                              context=context)
        if not warehouse_ids:
            raise osv.except_osv(_('Error!'),  _('No Warehouse available for the location: "%s"') % \
                                    (location.name))
        warehouse_obj = warehouse_pool.browse(cr, uid, warehouse_ids[0], context=context)
        warehouse_journal_id = warehouse_obj.journal_id and warehouse_obj.journal_id.id or False
        if not warehouse_journal_id:
            raise osv.except_osv(_('Error!'), _('There is no journal defined on the warehouse: "%s"') % \
                                    (warehouse_obj.name))
        try:
            journal_id, acc_src, acc_dest, acc_valuation = super(stock_move,self)._get_accounting_data_for_valuation(cr, uid, move, context=context)
        except:
            accounts = product_obj.get_product_accounts(cr, uid, move.product_id.id, context)
            if move.location_id.valuation_out_account_id:
                acc_src = move.location_id.valuation_out_account_id.id
            else:
                acc_src = accounts['stock_account_input']
            if move.location_dest_id.valuation_in_account_id:
                acc_dest = move.location_dest_id.valuation_in_account_id.id
            else:
                acc_dest = accounts['stock_account_output']
            acc_valuation = accounts.get('property_stock_valuation_account_id', False)
            if acc_dest == acc_valuation:
                raise osv.except_osv(_('Error!'),  _('Can not create Journal Entry, Output Account defined on this product and Valuation account on category of this product are same.'))
            if acc_src == acc_valuation:
                raise osv.except_osv(_('Error!'),  _('Can not create Journal Entry, Input Account defined on this product and Valuation account on category of this product are same.'))
            if not acc_src:
                raise osv.except_osv(_('Error!'),  _('There is no stock input account defined for this product or its category: "%s" (id: %d)') % \
                                        (move.product_id.name, move.product_id.id,))
            if not acc_dest:
                raise osv.except_osv(_('Error!'),  _('There is no stock output account defined for this product or its category: "%s" (id: %d)') % \
                                        (move.product_id.name, move.product_id.id,))
            if not acc_valuation:
                raise osv.except_osv(_('Error!'), _('There is no inventory Valuation account defined on the product category: "%s" (id: %d)') % \
                                        (move.product_id.categ_id.name, move.product_id.categ_id.id,))
        return warehouse_journal_id, acc_src, acc_dest, acc_valuation
stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
