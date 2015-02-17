##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import time

class stock_partial_picking(osv.osv_memory):
    
    _inherit = "stock.partial.picking"
    
    def do_partial(self, cr, uid, ids, context=None):
        res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)
        picking_ids = context.get('active_ids', False)
        self._create_production_lot(cr, uid, picking_ids, context=context)
        return res
    
    def _create_production_lot(self, cr, uid, picking_ids, context=None):
        pick_obj = self.pool.get('stock.picking').browse(cr, uid, picking_ids[0], context=context)
        count_lot={}
        count_kit={}
        for move in pick_obj.move_lines:
            if move.product_id.pack_fixed_price == False:
                if move.prodlot_id and pick_obj.sale_id and \
                   pick_obj.sale_id.service_order_ids:   
                      count_lot[move.prodlot_id.name] = move.product_qty
                      for service_order in pick_obj.sale_id.service_order_ids:
                          if service_order.order_line_ids:
                              qty = 0
                              for service_order_line in service_order.order_line_ids:
                                  loop_count = 0
                                  for pack in service_order_line.kit_id.pack_line_ids:
                                      loop_count = loop_count + 1
                                      if count_kit.get(str(service_order_line.id) + pack.product_id.name,False) == False :
                                       if count_lot[move.prodlot_id.name] > 0:
                                        if pack.product_id == move.product_id:
                                          count_kit[str(service_order_line.id) + pack.product_id.name] = pack.quantity 
                                          count_lot[move.prodlot_id.name] = count_lot[move.prodlot_id.name] - pack.quantity
                                          if loop_count == 1:
                                              sequence = move.prodlot_id.name
                                              if move.prodlot_id.prefix:
                                                  sequence = move.prodlot_id.prefix + '/' + sequence
                                              if move.prodlot_id.ref:
                                                  sequence = '%s [%s]' % (sequence, move.prodlot_id.ref)  
                                              self.pool.get('service.order.line').write(cr,uid,service_order_line.id,
                                                  { 'production_lot_ids': [(4, move.prodlot_id.id)],
                                                  'serial_number': sequence }, context=context)  
                                          else:    
                                              self.pool.get('service.order.line').write(cr,uid,service_order_line.id,
                                              { 'production_lot_ids': [(4, move.prodlot_id.id)] }, context=context)
                                        else:
                                            loop_count = loop_count - 1
        return True                       
       
stock_partial_picking()