# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2011 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
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
from osv import fields, osv
from tools.translate import _

class sale_order(osv.osv):
    _inherit="sale.order"

    def action_wait(self, cr, uid, ids, *args):

        template_ids = self.pool.get('email.template').search(cr,uid,[('object_name.model','=','sale.order')])
        res = super(sale_order, self).action_wait(cr, uid, ids, *args)
        if template_ids:
            for obj in self.browse(cr,uid,ids):
                if obj.partner_id.name != obj.partner_id.property_account_receivable.name:
                    self.pool.get('email.template').generate_mail(cr,uid,template_ids[0],ids,None)
        return res
sale_order()

class purchase_order(osv.osv):
    _inherit="purchase.order"

    def wkf_approve_order(self, cr, uid, ids, context=None):
         template_ids = self.pool.get('email.template').search(cr,uid,[('object_name.model','=','purchase.order')])
         res = super(purchase_order, self).wkf_approve_order(cr, uid, ids, context=context)
         if template_ids:
             for obj in self.browse(cr,uid,ids):
                if obj.partner_id.name != obj.partner_id.property_account_payable.name:
                    self.pool.get('email.template').generate_mail(cr,uid,template_ids[0],ids,None)
         return res
purchase_order()

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def action_date_assign(self, cr, uid, ids, *args):
        res = super(account_invoice, self).action_date_assign(cr, uid, ids, *args)
        for obj in self.browse(cr,uid,ids):
            if (obj.type=='out_invoice') | (obj.type=='in_invoice'):
                if obj.partner_id.name != obj.account_id.name:
                    raise osv.except_osv(_('Account Error'), _('The account of this partner is not a valid account'))
        return res
account_invoice()
