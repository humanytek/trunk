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

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

class non_deductible_expense_detail(osv.osv):
    _name = "nondeductible.expense"
    _description = "Non Deductible Expense Details"
    _rec_name = "expense_name"
    def _get_currency(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, [uid], context=context)[0]
        if 'company' in context:
            return self.pool.get('res.company').browse(cr,uid,context['company'],context=context).currency_id.id

        elif user.company_id:
                return user.company_id.currency_id.id
        return self.pool.get('res.currency').search(cr, uid, [('rate','=', 1.0)])[0]

    def onchange_currency(self, cr, uid, ids, currency_id=False, context=None):
        res = {}
        if not currency_id :
            res['value'] = {'rate': 0.0 }
            return res
        else:
            obj_currency = self.pool.get('res.currency')
            rate = obj_currency.browse(cr, uid, currency_id, context=context).rate
            res['value'] = {'rate': rate, }
            return res
    def unit_exp(self,cr,uid,ids,name,context=None,*args):
        res = {}
        for expense_line in self.browse(cr,uid,ids,context=None):
            res[expense_line.id]= expense_line.amount*expense_line.rate
        return res
    _columns = {
                'expense_name' : fields.char('Expense Name', size=64),
                'amount' : fields.float('Amount',digits_compute= dp.get_precision('Purchase Price')),
                'order_id' : fields.many2one('purchase.order','Expense Id'),
                'invoice_id' : fields.many2one('account.invoice','Expense Id'),
                'currency_id': fields.many2one('res.currency', 'Currency', required=True,),
                'rate':fields.float('Exchange Rate',digits=(12,6)),
                'amount_in_comp_currency':fields.function(unit_exp,method=True,type='float',string='Expense in company currency '),
                }
    _defaults = {
            'currency_id': _get_currency,

                 }
non_deductible_expense_detail()

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def action_invoice_create(self, cr, uid, ids, *args):
        res=super(purchase_order, self).action_invoice_create(cr, uid, ids, *args)
        for id in ids:
            ded_expense_ids=self.pool.get('nondeductible.expense').search(cr,uid,[('order_id','=',id)])
            if ded_expense_ids:
                self.pool.get('nondeductible.expense').write(cr,uid,ded_expense_ids,{'invoice_id' : res})
        return res

    def _total_amount_calc(self,cr,uid,ids,name,context=None,*args):
        res = {}
        non_ded_obj = self.pool.get('nondeductible.expense')
        orders = self.browse(cr,uid,ids,context=context)
        for order in self.browse(cr,uid,ids,context=context):
            non_ded_total = 0.00
            for line in order.nondeduct_ids:
                non_ded_total += line.amount*line.rate
            res[order.id] = non_ded_total
        return res

    def _get_ids(self,cr,uid,ids,context=None):
        purchase_order_ids = []
        for availability in self.pool.get('nondeductible.expense').browse(cr, uid, ids, context):
            if availability.order_id and availability.order_id.id not in purchase_order_ids:
                purchase_order_ids.append(availability.order_id.id)
        return purchase_order_ids

    def _total_quanity_calc(self,cr,uid,ids,name,context=None,*args):
        res = {}
        for order in self.browse(cr,uid,ids,context=None):
            qty=0
            for line in order.order_line :
                qty+=line.product_qty
            res[order.id] = qty
        return res
    _columns = {
                'nondeduct_ids' : fields.one2many('nondeductible.expense','order_id','Non deductible Expense Details',states={'approved':[('readonly',True)],'done':[('readonly',True)]}),
                'total_quantity' : fields.function(_total_quanity_calc,method=True,type='float',string='Total Quantity'),
                'nonded_total' : fields.function(_total_amount_calc,method=True,digits_compute= dp.get_precision('Purchase Price'),type='float',string='Total Expense in Company currency',help="Amount in company currency",
                                                 store={'nondeductible.expense':(_get_ids,['amount'],20)
                                                        })

                }
purchase_order()

class invoice_inherit_test(osv.osv):
    _inherit = "account.invoice"
    _columns = {
                'expences_ids' : fields.one2many('nondeductible.expense','invoice_id','Non deductible Expense Details'),

                }
invoice_inherit_test()

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    def _total_unit_price_exp(self,cr,uid,ids,name,context=None,*args):
        res = {}
        for order_line in self.browse(cr,uid,ids,context=None):
            currency_id = order_line.order_id.pricelist_id.currency_id.id
            company_id=order_line.company_id.id
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)
            expense_per_unit=0
            total_unit_price_exp=0
            if order_line.order_id and order_line.order_id.nonded_total and order_line.order_id.total_quantity :
                total_unit_price_exp=order_line.order_id.nonded_total/order_line.order_id.total_quantity
                new_price = order_line.price_unit / currency.rate
                expense_per_unit=new_price + total_unit_price_exp
            res[order_line.id]= expense_per_unit
        return res
    _columns = {
                'total_unit_price_exp' : fields.function(_total_unit_price_exp,method=True,type='float',string='Expense per unit(Company currency) ',help="Unit price + expense per unit in company currency "),

                }
purchase_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
