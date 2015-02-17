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
from tools.translate import _
import netsvc

class contract_make_invoice(osv.osv_memory):
    _name = "contract.make.invoice"
    _description = "Contract Make_invoice"
    _columns={
            'partner_id':fields.many2one('res.partner','Customer'),
            'sale_order_id':fields.many2one('sale.order','Sale Order',readonly=True),
            'product_id':fields.many2one('product.product','Product'),
            'qty':fields.float('Interval Quantity'),
            'intervel_unit':fields.selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], 'Interval Unit'),
            'unit_price':fields.float('Price'),
            'contract_id':fields.many2one('sale.contract','Contract')

              }
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res={}
        journal_obj = self.pool.get('account.journal')
        contract_obj = self.pool.get('sale.contract')
        res = super(contract_make_invoice, self).default_get(cr, uid, fields, context=context)
        active_id = context and context.get('active_id', False)
        if active_id:
            contract = contract_obj.browse(cr, uid, active_id, context=context)
            res.update({'contract_id': active_id})
            res.update({'partner_id': contract.partner_id.id})
            price = contract.contract_type_id.product_id.list_price
            res.update({'unit_price': price})
            res.update({'sale_order_id': contract.sale_order_id.id})
            res.update({'product_id': contract.contract_type_id.product_id.id})
            res.update({'intervel_unit': contract.contract_type_id.invoice_intervel_unit})
            res.update({'qty': contract.contract_type_id.invoice_qty})
        return res

    def make_invoices(self, cr, uid, ids, context=None):
        """
             To make invoices.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: A dictionary which of fields with values.

        """

        res = False
        invoices = {}
        def make_invoice(contract,order, lines):
            """
                 To make invoices.

                 @param order:
                 @param lines:

                 @return:

            """
            a = order.partner_id.property_account_receivable.id
            if order.partner_id and order.partner_id.property_payment_term.id:
                pay_term = order.partner_id.property_payment_term.id
            else:
                pay_term = False
            inv = {
                'name': contract.name,
                'origin': order.name,
                'type': 'out_invoice',
                'reference': "P%dC%dSO%d" % (order.partner_id.id,contract.id, order.id),
                'account_id': a,
                'partner_id': order.partner_id.id,
                'address_invoice_id': order.partner_invoice_id.id,
                'address_contact_id': order.partner_invoice_id.id,
                'invoice_line': [(6, 0, lines)],
                'currency_id' : order.pricelist_id.currency_id.id,
                'comment': order.note,
                'payment_term': pay_term,
                'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            }
            inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
            return inv_id

        contract_obj = self.pool.get('sale.contract')
        active_id = context and context.get('active_id', False)

        for line in self.browse(cr,uid,ids):
            if not line.sale_order_id.id in invoices:
                invoices[line.sale_order_id.id] = []
            if not active_id:
                active_id=line.contract_id.id
            line_id = contract_obj.invoice_line_create(cr, uid,[active_id])
            for lid in line_id:
                invoices[line.sale_order_id.id].append((line, lid))
        contract = contract_obj.browse(cr,uid,active_id)
        for result in invoices.values():
            order = result[0][0].sale_order_id

            il = map(lambda x: x[1], result)
            res = make_invoice(contract,order, il)

        return {'type': 'ir.actions.act_window_close'}

contract_make_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: