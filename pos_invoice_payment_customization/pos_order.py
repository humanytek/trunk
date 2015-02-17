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

import netsvc
from tools.translate import _

class pos_order(osv.osv):
    _inherit = 'pos.order'
    
    def action_invoice(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        product_obj = self.pool.get('product.product')
        inv_ids = []

        for order in self.pool.get('pos.order').browse(cr, uid, ids, context=context):
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue
            if not order.partner_id:
                raise osv.except_osv(_('Error'), _('Please provide a partner for the sale.'))
            acc = order.partner_id.property_account_receivable.id
            move_id = False
            for statement_line_obj in order.statement_ids:
                for account_move in statement_line_obj.move_ids:
                    move_id = account_move.id
            inv = {
                'name': order.name,
                'origin': order.name,
                'account_id': acc,
                'journal_id': order.sale_journal.id or None,
                'type': 'out_invoice',
                'reference': order.name,
                'partner_id': order.partner_id.id,
                'comment': order.note or '',
                'reconciled': True,
                'move_id': move_id,
                'currency_id': order.pricelist_id.currency_id.id, # considering partner's sale pricelist's currency
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', order.partner_id.id)['value'])
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(cr, uid, inv, context=context)

            self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'}, context=context)
            inv_ids.append(inv_id)
            for line in order.lines:
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                }
                inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=context)[0][1]
                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                                                               line.product_id.id,
                                                               line.product_id.uom_id.id,
                                                               line.qty, partner_id = order.partner_id.id,
                                                               fposition_id=order.partner_id.property_account_position.id)['value'])
                if line.product_id.description_sale:
                    inv_line['note'] = line.product_id.description_sale
                inv_line['price_unit'] = line.price_unit
                inv_line['discount'] = line.discount
                inv_line['name'] = inv_name
                inv_line['invoice_line_tax_id'] = ('invoice_line_tax_id' in inv_line)\
                    and [(6, 0, inv_line['invoice_line_tax_id'])] or []
                inv_line_ref.create(cr, uid, inv_line, context=context)
            wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
            inv_ref.button_reset_taxes(cr, uid, [inv_id], context=context)
        if not inv_ids: return {}
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False
        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': inv_ids and inv_ids[0] or False,
        }
    
    def create_from_ui(self, cr, uid, orders, context=None):
        partner_pool = self.pool.get('res.partner')
        statement_line_pool = self.pool.get('account.bank.statement.line')
        for order in orders:
            partner_id = order.get('partner_id', False)
            if partner_id:
                partner_obj = partner_pool.browse(cr, uid, int(partner_id), context=context)
                partner_account = partner_obj.property_account_receivable.id
                for statement_line_data in order.get('statement_ids', []):
                    line_data = statement_line_data[2]
                    line_data.update({'account_id': partner_account, 'partner_id': partner_id,})
        res = super(pos_order, self).create_from_ui(cr, uid, orders, context=context)
        for order_obj in self.browse(cr, uid, res, context=context):
            statement_line_objs = order_obj.statement_ids
            self.create_journal_entries(cr, uid, statement_line_objs, context=context)
        return res
    
    def create_journal_entries(self, cr, uid, statement_line_objs, context=None):
        if context is None:
            context = {}
        obj_seq = self.pool.get('ir.sequence')
        res_currency_obj = self.pool.get('res.currency')
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        account_bank_statement_obj = self.pool.get('account.bank.statement')
        property_obj = self.pool.get('ir.property')
        for statement_line_obj in statement_line_objs:
            statement_obj = statement_line_obj.statement_id
            company_currency_id = statement_obj.journal_id.company_id.currency_id.id
            if not statement_obj.name == '/':
                st_number = statement_obj.name
            else:
                c = {'fiscalyear_id': statement_obj.period_id.fiscalyear_id.id}
                if statement_obj.journal_id.sequence_id:
                    st_number = obj_seq.next_by_id(cr, uid, statement_obj.journal_id.sequence_id.id, context=c)
                else:
                    st_number = obj_seq.next_by_code(cr, uid, 'account.bank.statement', context=c)
            st_line_number = account_bank_statement_obj.get_next_st_line_number(cr, uid, st_number, statement_line_obj, context=context)
            context.update({'date': statement_line_obj.date})
            if statement_line_obj.analytic_account_id:
                if not statement_line_obj.statement_id.journal_id.analytic_journal_id:
                    raise osv.except_osv(_('No Analytic Journal !'),_("You have to assign an analytic journal on the '%s' journal!") % (st.journal_id.name,))
            if not statement_line_obj.amount:
                continue
            move_id = account_bank_statement_obj.create_move_from_st_line(cr, uid, statement_line_obj.id, company_currency_id, st_line_number, context=context)
            move_obj = account_move_obj.browse(cr, uid, move_id, context=context)
            account_def = property_obj.get(cr, uid, 'property_account_receivable', 'res.partner', context=context)
            account_id = statement_line_obj.partner_id and statement_line_obj.partner_id.property_account_receivable and\
                            statement_line_obj.partner_id.property_account_receivable.id or account_def.id
            moveline_id = [x.id for x in move_obj.line_id if x.account_id.id == account_id]
            context['fy_closing'] = True
            account_move_line_obj.reconcile(cr, uid, moveline_id, context=context)
        return True
    
pos_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
