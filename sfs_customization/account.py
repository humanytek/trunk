# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2011 ZestyBeanz Technologies Pvt. Ltd.
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
##
##############################################################################

import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    def action_date_assign(self, cr, uid, ids, *args):
        for inv in self.browse(cr, uid, ids):
            if inv.type == 'out_invoice':
               cr.execute("SELECT order_id FROM sale_order_invoice_rel WHERE invoice_id=%s",(inv.id,))
               res = cr.fetchone()
               if res and res[0] :
                   sale_obj=self.pool.get('sale.order').browse(cr,uid,res[0])
                   if sale_obj.user_id:
                       self.write(cr, uid, [inv.id], {'user_id':sale_obj.user_id.id })
                       #raise osv.except_osv(_('Invalid action !'), _(' You cannot validate this invoices. The salesman is different in invoice and its related Sale !'))
                   if sale_obj.user_id and uid == sale_obj.user_id.id:
                       raise osv.except_osv(_('Invalid action !'), _(' You cannot validate this invoice since you closed this Sale !'))

            res = self.onchange_payment_term_date_invoice(cr, uid, inv.id, inv.payment_term.id, inv.date_invoice)
            if res and res['value']:
                self.write(cr, uid, [inv.id], res['value'])
            res = self.onchange_payment_term_date_invoice(cr, uid, inv.id, inv.payment_term.id, inv.date_invoice)
            if res and res['value']:
                self.write(cr, uid, [inv.id], res['value'])
        return True

account_invoice()