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
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
import netsvc

class patient_prescription_order (osv.osv):
    _inherit="medical.prescription.order"

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_paid': 0.0,
                'amount_return':0.0,
                'amount_tax':0.0,
            }

            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            #for payment in order.statement_ids:
             #   res[order.id]['amount_paid'] +=  payment.amount
              #  res[order.id]['amount_return'] += (payment.amount < 0 and payment.amount or 0)
            for line in order.prescription_line:
                val1 += line.subtotal

                if order.price_type != 'tax_excluded':
                    res[order.id]['amount_tax'] = reduce(lambda x, y: x+round(y['amount'], 2),
                        tax_obj.compute_inv(cr, uid, line.tax_id,
                            line.price_unit * \
                            (1-(line.discount or 0.0)/100.0), line.quantity),
                            res[order.id]['amount_tax'])
                if line.quantity != 0.0:
                    for c in tax_obj.compute_all(cr, uid, line.tax_id, \
                                                 line.price_unit * (1-(line.discount or 0.0)/100.0), \
                                                 line.quantity,  line.medicament, line.name.name)['taxes']:
                        val += c.get('amount', 0.0)

            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_total'] = res[order.id]['amount_tax'] + cur_obj.round(cr, uid, cur, val1)
        return res

    def _sale_journal_get(self, cr, uid, context=None):
        """ To get  sale journal for this order
        @return: journal  """
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', 'sale')], limit=1)
        return res and res[0] or False

    _columns = {
                'state': fields.selection([('draft', 'Draft'),('confirmed', 'Confirmed'),('done', 'Done'),('cancel', 'Cancelled')], 'State', required=True, readonly=True,),
                'shop_id':fields.many2one('sale.shop','Shop'),
                'picking_id':fields.many2one('stock.picking','Picking'),
                #'partner_id': fields.many2one('res.partner', 'Customer', change_default=True, select=1, ),
                'statement_ids': fields.one2many('account.bank.statement.line', 'pos_id', 'Payments', states={'draft': [('readonly', False)]}, readonly=True),
                'sale_journal': fields.many2one('account.journal', 'Journal', required=True, states={'draft': [('readonly', False)]}, readonly=True),
                'journal_entry': fields.boolean('Journal Entry'),
                'price_type': fields.selection([
                                ('tax_excluded','Tax excluded')],
                                 'Price method', ),
                'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, ),
                'amount_tax': fields.function(_amount_all, method=True, string='Taxes', digits_compute=dp.get_precision('Point of Sale'), multi='all'),
                'amount_total': fields.function(_amount_all, method=True, string='Total', multi='all'),
                'stock_lines' :fields.one2many('stock.picking','prescription_id','Picking'),
                'prescription_line' : fields.one2many ('medical.prescription.line', 'name', 'Prescription line',states={'draft': [('readonly', False)]}, readonly=True),
                'insurance_id' :fields.many2one('medical.insurance', 'Insurance' ),
                'patient_id' : fields.many2one('res.partner','Patient'),

               }


    def _select_pricelist(self, cr, uid, context=None):
        """ To get default pricelist for the order
        @param name: Names of fields.
        @return: pricelist ID
        """
        res = self.pool.get('sale.shop').search(cr, uid, [], context=context)
        if res:
            shop = self.pool.get('sale.shop').browse(cr, uid, res[0], context=context)
            return shop.pricelist_id and shop.pricelist_id.id or False
        return False

    def onchange_name(self,cr,uid,ids,name,patient_id,insurance_id):
        result={}

        if name:
            patient=self.pool.get('medical.patient').browse(cr,uid,name)
            return {'value':{'patient_id':patient.name.id,'insurance_id':False}}
        return {}





    _defaults = {
                 'state': 'draft',
                 'pricelist_id': _select_pricelist,
                 'sale_journal': _sale_journal_get,

                 }


    def test_paid(self, cr, uid, ids, context=None):
        """ Test all amount is paid for this order
        @return: True
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.prescription_line and not order.amount_total:
                return True
            #if (not order.prescription_line) or (not order.statement_ids) or \
             #   Decimal(str(order.amount_total)) != Decimal(str(order.amount_paid)):
              #  return False
        return True

    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        property_obj = self.pool.get("ir.property")
        move_obj=self.pool.get('stock.move')
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            if not order.picking_id:
                new = True
                picking_id = picking_obj.create(cr, uid, {
                    'name': pick_name,
                    'origin': order.prescription_id,
                    'type': 'out',
                    'state': 'draft',
                    'move_type': 'direct',
                    'note': 'pharmacy notes ' + (order.notes or ""),
                    'invoice_state': 'none',
                    'auto_picking': True,
                    'prescription_id':order.id,

                }, context=context)
                self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
            else:
                picking_id = order.picking_id.id
                picking_obj.write(cr, uid, [picking_id], {'auto_picking': True}, context=context)
                picking = picking_obj.browse(cr, uid, [picking_id], context=context)[0]
                new = False

                # split the picking (if product quantity has changed):
#                diff_dict = self._get_qty_differences(orders, picking)
#                if diff_dict:
#                    self._split_picking(cr, uid, ids, context, picking, diff_dict)

            if new:
                for line in order.prescription_line:
                    if line.medicament.name and line.medicament.name.type == 'service':
                        continue
                    prop_ids = property_obj.search(cr, uid, [('name', '=', 'property_stock_customer')], context=context)
                    val = property_obj.browse(cr, uid, prop_ids[0], context=context).value_reference
                    cr.execute("SELECT s.id FROM stock_location s, stock_warehouse w WHERE w.lot_stock_id = s.id AND w.id = %s", (order.shop_id.warehouse_id.id, ))
                    res = cr.fetchone()
                    location_id = res and res[0] or None
                    stock_dest_id = val.id
                    if line.quantity < 0:
                        location_id, stock_dest_id = stock_dest_id, location_id
                    print">>>>>>>>>>>>>>>>>>",line.medicament.name.name
                    move_obj.create(cr, uid, {
                            'name': line.medicament.name.name,
                            'product_uom': line.medicament.name.uom_id.id,
                            'product_uos': line.medicament.name.uom_id.id,
                            'picking_id': picking_id,
                            'product_id': line.medicament.name.id,
                            'product_uos_qty': abs(line.quantity),
                            'product_qty': abs(line.quantity),
                            'tracking_id': False,
                            'pos_line_id': line.id,
                            'state': 'waiting',
                            'location_id': location_id,
                            'location_dest_id': stock_dest_id,
                            'ret_qty':abs(line.ret_qty)
                        }, context=context)

            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            picking_obj.force_assign(cr, uid, [picking_id], context)
        return True

    def action_paid(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('flag', False):
            self.create_picking(cr, uid, ids, context=None)
            self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
        else:
            context['flag'] = True
        return True

    def order_confirm(self,cr,uid,ids,context):
        move_id=self.create_picking(cr,uid,ids,context)
        self.write(cr,uid,ids,{"state" : 'confirmed'})
        return True

    def order_cancel(self,cr,uid,ids,context):
        self. write(cr,uid,ids,{'state':'cancel'})
        return True

    def add_payment(self, cr, uid, order_id, data, context=None):
        """Create a new payment for the order"""
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        prod_obj = self.pool.get('product.product')
        property_obj = self.pool.get('ir.property')
        curr_c = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        curr_company = curr_c.id
        order = self.browse(cr, uid, order_id, context=context)
        #if not order.num_sale and data['num_sale']:
         #   self.write(cr, uid, order_id, {'num_sale': data['num_sale']}, context=context)
        ids_new = []
        args = {
            'amount': data['amount'],
        }
        if 'payment_date' in data.keys():
            args['date'] = data['payment_date']
        if 'payment_name' in data.keys():
            args['name'] = data['payment_name'] + ' ' + order.prescription_id
        account_def = property_obj.get(cr, uid, 'property_account_receivable', 'res.partner', context=context)
        args['account_id'] = order.name.name and order.name.name.property_account_receivable \
                             and order.name.name.property_account_receivable.id or account_def.id or curr_c.account_receivable.id
        #if data.get('is_acc', False):
         #   args['is_acc'] = data['is_acc']
          #  args['account_id'] = prod_obj.browse(cr, uid, data['product_id'], context=context).property_account_income \
           #                      and prod_obj.browse(cr, uid, data['product_id'], context=context).property_account_income.id
            #if not args['account_id']:
             #   raise osv.except_osv(_('Error'), _('Please provide an account for the product: %s')% \
              #                       (prod_obj.browse(cr, uid, data['product_id'], context=context).name))
        args['partner_id'] = order.name.name and order.name.name.id or None
        args['ref'] = order.prescription_id#order.contract_number or None

        statement_id = statement_obj.search(cr,uid, [
                                                     ('journal_id', '=', data['journal']),
                                                     ('company_id', '=', curr_company),
                                                     ('user_id', '=', uid),
                                                     ('state', '=', 'open')], context=context)


        if len(statement_id) == 0:
            raise osv.except_osv(_('Error !'), _('You have to open at least one cashbox'))
        if statement_id:
            statement_id = statement_id[0]
        args['statement_id'] = statement_id
        args['pos_id'] = order_id
        args['journal_id'] = data['journal']
        args['type'] = 'customer'
        args['ref'] = order.prescription_id

        statement_line_obj.create(cr, uid, args, context=context)
        ids_new.append(statement_id)

        #wf_service = netsvc.LocalService("workflow")
        #wf_service.trg_validate(uid, 'pos.order', order_id, 'paid', cr)
        #wf_service.trg_write(uid, 'pos.order', order_id, cr)

        return statement_id

    def action_invoice(self, cr, uid, ids, context=None):

        """Create a invoice of order  """

        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        product_obj = self.pool.get('product.product')
        inv_ids = []

        for order in self.pool.get('medical.prescription.order').browse(cr, uid, ids, context=context):
            #if order.invoice_id:
             #   inv_ids.append(order.invoice_id.id)
              #  continue

            if not order.name.name:
                raise osv.except_osv(_('Error'), _('Please provide a partner for the sale.'))

            acc = order.name.name.property_account_receivable.id

            inv = {
                'name': 'Invoice from POS: ' +order.prescription_id,
                'origin': order.prescription_id,
                'account_id': acc,
                'journal_id': order.sale_journal.id or None,
                'type': 'out_invoice',
                'reference': order.prescription_id,
                'partner_id': order.name.name.id,
                'comment': order.notes or '',
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', order.name.name.id)['value'])
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(cr, uid, inv, context=context)

            self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'done'}, context=context)
            inv_ids.append(inv_id)
            for line in order.prescription_line:
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': line.medicament.name.id,
                    'quantity': line.quantity,
                }
                inv_name = product_obj.name_get(cr, uid, [line.medicament.name.id], context=context)[0][1]

                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                                                               line.medicament.name.id,
                                                               line.medicament.name.uom_id.id,
                                                               line.quantity, partner_id = order.name.name.id,
                                                               fposition_id=order.name.name.property_account_position.id)['value'])
                inv_line['price_unit'] = line.price_unit
                inv_line['discount'] = line.discount
                inv_line['name'] = inv_name

                inv_line['invoice_line_tax_id'] = [(6, 0, [x.id for x in line.tax_id])]#('invoice_line_tax_id' in inv_line)\
                    #and [(6, 0, inv_line['invoice_line_tax_id'])] or []

                inv_line_ref.create(cr, uid, inv_line, context=context)

        for i in inv_ids:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice', i, 'invoice_open', cr)
        return inv_ids



    def action_done(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if not order.journal_entry:

                self.create_account_move(cr, uid, ids, context=None)
        return True

patient_prescription_order()

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'

    def _get_statement_journal(self, cr, uid, ids, context, *a):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.statement_id and line.statement_id.journal_id and line.statement_id.journal_id.name or None
        return res

    _columns= {
        'journal_id': fields.function(_get_statement_journal, method=True,store=True, string='Journal', type='char', size=64),
        #'am_out': fields.boolean("To count"),
        #'is_acc': fields.boolean("Is accompte"),
        'pos_id': fields.many2one('medical.prescription.order','Order', ondelete='cascade'),
    }
account_bank_statement_line()


class prescription_line (osv.osv):
    _inherit="medical.prescription.line"

    def _total_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total_amount = 0
        for line in self.browse(cr, uid, ids):
            if line.price_unit and line.quantity:
                total_amount=line.price_unit*line.quantity
                res[line.id]=total_amount
            else:
                res[line.id]=total_amount
        return res


    def _total_amount_incl(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total_amount = 0
        for line in self.browse(cr, uid, ids):
            if line.price_unit and line.quantity:
                if not line.tax_id:
                    total_amount=line.price_unit*line.quantity
                    res[line.id]=total_amount
                else:
                    price=line.price_unit
                    for tax in line.tax_id:
                        price=price+(line.price_unit*(tax.amount))
                    total_amount=price*line.quantity
                    res[line.id]=total_amount
            else:
                res[line.id]=total_amount
        return res




    _columns = {
                'product_id':fields.many2one ('product.product','Name', domain=[('is_medicament', '=', "1")],help="Commercial Name"),
                'tax_id': fields.many2many('account.tax', 'pharma_sale_order_tax', 'order_line_id', 'tax_id', 'Taxes'),
                'ret_qty':fields.integer('Returned Quantity'),
                'price_unit': fields.float('Unit Price', digits_compute= dp.get_precision('Sale Price')),
                'subtotal':fields.function(_total_amount, method=True, string='Subtotal w/o Tax', type="float"),
                'subtotal_incl': fields.function(_total_amount_incl, method=True, type="float", string='Subtotal'),
                'discount': fields.float('Discount (%)', digits=(16, 2)),
                'insurance_id' :fields.many2one('medical.insurance', 'Insurance' ),
                'invoice_status' : fields.selection([('invoiced','Invoiced'),('tobe','To be Invoiced')],'Invoice Status'),
               }

    def _get_insurance(self, cr, uid, context=None):

        if 'insurance_id' in context:
            return context['insurance_id']
        return {}

    _defaults={'ret_qty':lambda *a :0,
               'insurance_id': _get_insurance,
               'invoice_status':lambda *a :'tobe',
               }

    def onchange_medicament(self,cr,uid,ids,medicament,shop_id,context=None):
        if not  shop_id:
            raise osv.except_osv(_('No Shop Defined !'), _('You have to select a shop in the sales form !\nPlease set one shop before choosing a product.'))
        if not medicament :
            return {'value': {'product_id': False, 'price_unit': 0.0,'tax_id': False}}
        else:
            medicament_obj=self.pool.get('medical.medicament').browse(cr,uid,medicament)

            product_id=medicament_obj.name.id
            price=medicament_obj.name.list_price

            result = {}
            fpos =  False
            product_obj = self.pool.get('product.product')
            product_obj = product_obj.browse(cr, uid, product_id)

            result['product_id']=medicament_obj.name.id
            result['price_unit']=medicament_obj.name.list_price
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        return {'value':result }

prescription_line()
