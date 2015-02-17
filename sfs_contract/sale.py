# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 ZestyBeanz Technologies Pvt. Ltd.
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
from datetime import datetime
import time
from tools.translate import _

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns={
              'contract_ids' : fields.one2many('sale.contract','sale_order_id','Contract Ids',readonly=True)
              }

sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns={
              'contract':fields.boolean('Contract',help="Check if you want to create contract"),
              'contract_type_id':fields.many2one('sale.contract.type','Contract Type')
              }
    _defaults={
            'contract':lambda*a:False
               }

    def button_confirm(self, cr, uid, ids, context=None):
        res = super(sale_order_line, self).button_confirm(cr, uid, ids, context=context)
        contract_pool = self.pool.get('sale.contract')
        for obj in self.browse(cr,uid,ids):
            if obj.contract:
                data = {
                    'contract_type_id':obj.contract_type_id.id,
                    'product_id' : obj.product_id.id,
                    'partner_id':obj.order_partner_id.id,
                    'sale_order_id':obj.order_id.id,
                    'sale_order_line_id':obj.id,
                    'qty' : obj.contract_type_id.qty,
                    'intervel_unit' : obj.contract_type_id.intervel_unit,
                    'invoice_qty' : obj.contract_type_id.invoice_qty,
                    'invoice_intervel_unit' : obj.contract_type_id.invoice_intervel_unit,
                    'invoice_create' : obj.contract_type_id.invoice_create
                        }
                contract_pool.create(cr,uid,data)
        return res
sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: