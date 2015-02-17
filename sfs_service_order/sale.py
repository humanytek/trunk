# -*- coding: utf-8 -*-
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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import netsvc

class sale_order(osv.osv):
    _inherit ='sale.order'
    _columns = {
        'service_order_ids': fields.many2many('service.order', 'service_order_rel', 'sale_order_id', 'service_order_id', 'Service Order'),           
    } 
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'service_order_ids' : []
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)   
    
    def action_ship_create(self, cr, uid, ids, *args):
        res = super(sale_order, self).action_ship_create(cr, uid, ids)
        for order in self.browse(cr, uid, ids, context=None):
            self._create_service_order(cr, uid, order,context=None)
        return res
        
    
    def _prepare_service_order(self, cr, uid, order, picking_obj, context=None):
        return {
            'source_id': picking_obj.id,
            'customer_id': order.partner_id.id,
            'address_id': order.partner_shipping_id.id,
            'sale_order_id': order.id,
            'phone': order.partner_id.phone,
            'mobile': order.partner_id.mobile
        }
        
    def _create_service_order_line(self, cr, uid, service_order_id, product, context=None):
        service_order_line_id = self.pool.get('service.order.line').create(cr, uid, {'service_order_id': service_order_id},context=context)
        if service_order_line_id: 
            self.pool.get('service.order.line').write(cr,uid,service_order_line_id,{ 'kit_id': product.id }, context=context)
            for pack_line in product.pack_line_ids:
                self.pool.get('service.order.line').write(cr,uid,service_order_line_id,{ 'accessories_ids': [(4, pack_line.product_id.id)]}, context=context)
        return True    

    def _create_service_order(self, cr, uid, order,context=None):
        service_obj = self.pool.get('service.order')
        service_order_id = False
        if order.picking_ids:
            for picking_obj in order.picking_ids:
                for order_line_obj in order.order_line:
                    if order_line_obj.product_id.pack_fixed_price:
                        for x in range(0,int(order_line_obj.product_uom_qty)):
                            if not service_order_id:
                                service_order_id = service_obj.create(cr, uid, self._prepare_service_order(cr, uid, order, picking_obj, context=context))
                                self.pool.get('sale.order').write(cr,uid,order.id,{ 'service_order_ids': [(4, service_order_id)]}, context=context)
                            if service_order_id:
                                self._create_service_order_line(cr, uid, service_order_id, order_line_obj.product_id,context=None)
        return True

    
sale_order()
    