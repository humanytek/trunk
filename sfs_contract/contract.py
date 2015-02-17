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
from datetime import datetime, timedelta
import time
from dateutil.relativedelta import relativedelta
from tools.translate import _
import base64
import random
import netsvc
import re
import tools
import pooler
import logging

TEMPLATE_ENGINES = []

from osv import osv, fields
from tools.translate import _
try:
    from mako.template import Template as MakoTemplate
    TEMPLATE_ENGINES.append(('mako', 'Mako Templates'))
except ImportError:
    logging.getLogger('init').warning("module email_template: Mako templates not installed")

try:
    from django.template import Context, Template as DjangoTemplate
    from django.conf import settings
    settings.configure()
    TEMPLATE_ENGINES.append(('django', 'Django Template'))
except ImportError:
    logging.getLogger('init').warning("module email_template: Django templates not installed")




class contract_type(osv.osv):
    _name="sale.contract.type"
    _columns={
            'name':fields.char('Name',size=64,required=True),
            'product_id':fields.many2one('product.product','Product',required=True,),
            'qty':fields.integer('Interval Quantity',required=True,help="Specifies the day/month/week before which contract is renewed"),
            'intervel_unit': fields.selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], 'Interval Unit',help="Specifies the renewal day is specified in days,week or month"),
            'invoice_qty':fields.integer('Interval Quantity',required=True,help="Specifies the difference between two invoice printing dates"),
            'invoice_intervel_unit': fields.selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], 'Interval Unit',help="Specifies weather Invoice Interval Quantity specifies number of days, week or months"),
            'note':fields.text('Notes'),
            'active':fields.boolean('Active'),
            'invoice_create' : fields.selection([('first','On sign date'),('end','On first interval date')],'First Invoice On',required=True,help="Create invoice on contract sign date or on first interval date")
              }
    _defaults = {
            'qty':lambda *a:1,
            'invoice_qty':lambda *a:1,
            'active':lambda *a:True,
            'intervel_unit' : 'days',
            'invoice_intervel_unit' : 'days'
                }

    _sql_constraints = [
        ('qty_positive', 'CHECK(qty >= 1)', 'Interval Quantity should be greater than 0'),
        ('invoice_qty_positive', 'CHECK(invoice_qty >= 1)', 'Invoice Interval Quantity should be greater than 0')]


contract_type()

class contract(osv.osv):
    _name = "sale.contract"

    def _get_template(self, cr, uid, ids, name=None, args=None, context=None):
        res = {}
        pool = pooler.get_pool(cr.dbname)
        if context == None:
            context = {}
        if ids:
            for id in ids:
                reply = ''
                contract_obj = self.pool.get('sale.contract').browse(cr,uid,id,context=context)
                message = contract_obj.agreement_template_id.notes
                if message is None:
                    message = {}
                if message:
                    try:
                        message = tools.ustr(message)
                        object = pool.get('sale.contract').browse(cr, uid,id , context=context)
                        env = {
                            'user':pool.get('res.users').browse(cr, uid, uid, context=context),
                            'db':cr.dbname
                               }
                        templ = MakoTemplate(message, input_encoding='utf-8')
                        reply = MakoTemplate(message).render_unicode(object=object,
                                                                         peobject=object,
                                                                         env=env,
                                                                         format_exceptions=True)
                    except Exception:
                        logging.exception("can't render %r", message)
                        return u""
                res[contract_obj.id] = reply
        return res

    _columns={
            'name':fields.char('Contract Number',size=32,required=True),
            'contract_type_id':fields.many2one('sale.contract.type','Contract Type',required=True,readonly=True, states={'draft': [('readonly', False)]}),
            'date':fields.datetime('Elaboration Date',readonly=True),
            'sign_date':fields.datetime('Sign Date'),
            'expire_date':fields.datetime('Expiration Date',readonly=True),
            'expired':fields.boolean('Expired',readonly=True),
            'partner_id':fields.many2one('res.partner','Customer',required=True,readonly=True, states={'draft': [('readonly', False)]}),
            'sale_order_id':fields.many2one('sale.order','Sale Order',required=True,readonly=True, states={'draft': [('readonly', False)]}),
            'sale_order_line_id':fields.many2one('sale.order.line','Sale Order Line',),
            'automated_renew_date' : fields.datetime('Automated Date',readonly=True),
            'automated' : fields.boolean('Automated',readonly=True),
            'automated_renew':fields.boolean('Automated Renew'),
            'new_contract':fields.integer('Generate New Contract',help="Specifies the number of days",readonly=True, states={'draft': [('readonly', False)]}),
            'origin':fields.char('Source Document',size=128,readonly=True),
            'state':fields.selection([('draft','Draft'),
                                      ('active','Signed'),
                                      ('expired','Expired'),
                                      ('cancel','Cancelled')],'State',readonly=True),
            'product_id':fields.many2one('product.product','Product'),
            'qty':fields.integer('Quantity'),
            'intervel_unit':fields.selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], 'Interval Unit'),
            'invoice_qty':fields.integer('Quantity'),
            'invoice_intervel_unit':fields.selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], 'Interval Unit'),
            'next_invoice_date' : fields.datetime('Next Invoice Date',readonly=True),
            'renewed' : fields.boolean('Renewed'),
            'invoice_create' : fields.selection([('first','On sign date'),('end','On first interval date')],'Invoice On',help="Create invoice on contract sign date or on first interval date"),
            'invoice_ids' : fields.one2many('account.invoice','contract_id','Invoice(s)',readonly=True),
            'agreement_template_id' : fields.many2one('template.agreement', 'Special Agreement Template',readonly=True, states={'draft': [('readonly', False)]}),
            'agreement_template' : fields.function(_get_template, string="Special Agreement Template", method=True, type="text"),
            'reference': fields.related('partner_id', 'reference',string='Reference',type="char", size=128, readonly=True, store=True)
             }
    _defaults={
            'name':lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'sale.contract'),
            'date':lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
            'automated_renew':lambda*a:True,
            'new_contract':1,
            'state':'draft',
            'renewed' : False
               }

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Create the new record in contract model from existing one
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: list of record ids on which copy method executes
        @param default: dict type contains the values to be overridden during copy of object
        @param context: context arguments, like lang, time zone

        @return: Returns the id of the new record
        """
        if not default:
            default = {}
        default.update({
            'name':self.pool.get('ir.sequence').get(cr, uid, 'sale.contract'),
            'date':time.strftime('%Y-%m-%d %H:%M:%S'),
            'sign_date':False,
            'expire_date':False,
            'expired':False,

        })
        res_id = super(contract, self).copy(cr, uid, ids, default, context=context)
        return res_id

    def onchange_contract_type_id(self,cr,uid,ids,contract_type_id):
        res={}
        if not contract_type_id:
            return {}
        contract_type_inst = self.pool.get('sale.contract.type')
        contract_type_obj = self.pool.get('sale.contract.type').browse(cr,uid,contract_type_id,context=None)
        res['product_id'] = contract_type_obj.product_id.id
        res['qty'] = contract_type_obj.qty
        res['intervel_unit'] = contract_type_obj.intervel_unit
        res['invoice_qty'] = contract_type_obj.invoice_qty
        res['invoice_intervel_unit'] = contract_type_obj.invoice_intervel_unit
        res['invoice_create'] = contract_type_obj.invoice_create
        return {'value':res}

    def button_confirm(self,cr,uid,ids,context=None):
        automated_renew_date = False
        for sale_contract_obj in self.browse(cr,uid,ids,context=context):
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            sign_date = datetime.strptime(str(now),"%Y-%m-%d %H:%M:%S")
            qty = sale_contract_obj.qty
            intervel_unit = sale_contract_obj.intervel_unit
            invoice_qty = sale_contract_obj.invoice_qty
            invoice_intervel_unit = sale_contract_obj.invoice_intervel_unit
            invoice_create = sale_contract_obj.invoice_create
            new_contract = sale_contract_obj.new_contract
            if intervel_unit == 'months':
                expiry_date = (sign_date + relativedelta(months=qty))
            elif intervel_unit == 'weeks':
                expiry_date = (sign_date + relativedelta(weeks=qty))
            elif intervel_unit == 'days':
                expiry_date = (sign_date + relativedelta(days=qty))
            if sale_contract_obj.automated_renew:
                new_contract = sale_contract_obj.new_contract
                automated_renew_date = expiry_date - relativedelta(days=new_contract)
            if invoice_create == 'first':
                self.create_invoice(cr,uid,ids)
            if invoice_intervel_unit == 'months':
                next_invoice_date = (sign_date + relativedelta(months=invoice_qty))
            elif invoice_intervel_unit == 'days':
                next_invoice_date = (sign_date + relativedelta(days=invoice_qty))
            elif invoice_intervel_unit == 'weeks':
                next_invoice_date = (sign_date + relativedelta(weeks=invoice_qty))
            self.write(cr,uid,sale_contract_obj.id,{'state':'active','sign_date':sign_date,'expire_date':expiry_date,'automated_renew_date':automated_renew_date,'next_invoice_date':next_invoice_date})
        return True

    def button_cancel(self, cr, uid, ids, context=None):
        for contract_obj in self.browse(cr, uid, ids, context=context):
            if contract_obj.invoice_ids:
                raise osv.except_osv(_('Error'), _('This contract can not change state because it contains related invoices'))
        return self.write(cr, uid, ids, {'state': 'cancel'})
    
    def button_reactivate(self, cr, uid, ids, context=None):
        vals = {}
        vals = {
                'sign_date': False,
                'expire_date': False,
                'automated_renew_date': False,
                'next_invoice_date': False,
                'state': 'draft'
               }
        return self.write(cr, uid, ids, vals, context=context)

    def run_expired_contracts(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        """cron that search for expired contracts and mark its with expired everyday, send a notification too"""
        if context is None: context = {}
        today = time.strftime('%Y-%m-%d %H:%M:%S')
        ids = self.search(cr, uid, [('expire_date', '<', today), ('expired', '=', False),('state','=','active')])
        if ids:
            self.write(cr, uid, ids, {'state':'expired','expired':True})
            group_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', 'Contract / Expiration Notifications')])
            if group_id:
                group_id = group_id[0]
                cr.execute("select uid from res_groups_users_rel where gid = %s" % (group_id,))
                res = cr.fetchall()
                expired_lots_names = u','.join(map(str, map(lambda x:x.name, self.browse(cr, uid, ids))))
                message = _("New expired Contract.\n\nContract names: %s\n\n") % (expired_lots_names,)
                for (user_id,) in res:
                    self.pool.get('res.request').create(cr, uid, {
                            'name': _("Contract Expired"),
                            'body': message,
                            'state': 'waiting',
                            'act_from': uid,
                            'act_to': user_id,
                            'priority': '0'
                        })
        return True

    def run_renew_contract(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        if context is None: context = {}
        today = time.strftime('%Y-%m-%d %H:%M:%S')
        ids = self.search(cr, uid, [('automated_renew_date', '<', today),('renewed','=',False),('expired', '=', False), ('automated_renew','=',True), ('state','=','active')])# ('renewed','=',False),('expired', '=', False), ('automated_renew','=',True)]
        if ids:
            for sale_contract_obj in self.browse(cr,uid,ids,context=context):
                expire_date = datetime.strptime(str(sale_contract_obj.expire_date),"%Y-%m-%d %H:%M:%S")
                qty = sale_contract_obj.qty
                interval_unit = sale_contract_obj.intervel_unit
                orgin = str(sale_contract_obj.sale_order_id.name)+':'+str(sale_contract_obj.name)
                if interval_unit == 'months':
                    new_expire_date = (expire_date + relativedelta(months=qty))
                elif interval_unit == 'days':
                    new_expire_date = (expire_date + relativedelta(days=qty))
                elif interval_unit == 'weeks':
                    new_expire_date = (expire_date + relativedelta(weeks=qty))
                vals = {
                        'contract_type_id' : sale_contract_obj.contract_type_id.id,
                        'partner_id' : sale_contract_obj.partner_id.id,
                        'sale_order_id' : sale_contract_obj.sale_order_id.id,
                        'automated_renew' : True,
                        'date' : today,
                        'new_contract' : sale_contract_obj.new_contract,
                        'product_id' : sale_contract_obj.product_id.id,
                        'qty' : sale_contract_obj.qty,
                        'intervel_unit' : sale_contract_obj.intervel_unit,
                        'invoice_qty' : sale_contract_obj.invoice_qty,
                        'invoice_intervel_unit' : sale_contract_obj.intervel_unit,
                        'invoice_create' : sale_contract_obj.invoice_create,
                        'origin' : orgin
                        }
                new_id = self.create(cr,uid,vals,context=context)
                group_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', 'Contract / Expiration Notifications')])
                if group_id:
                    group_id = group_id[0]
                    cr.execute("select uid from res_groups_users_rel where gid = %s" % (group_id,))
                    res = cr.fetchall()
                    renew_contract = sale_contract_obj.name
                    message = _("Contract Renewed.\n\nContract names: %s\n\n") % (renew_contract,)
                    for (user_id,) in res:
                        self.pool.get('res.request').create(cr, uid, {
                                'name': _("Contract Renewed"),
                                'body': message,
                                'state': 'waiting',
                                'act_from': uid,
                                'act_to': user_id,
                                'priority': '0'
                            })
                self.write(cr,uid,ids,{'renewed' : True,'automated' : True})
        return True

    def create_invoice(self, cr, uid, ids, automatic=False, use_new_cursor=False, context=None):
        if context is None: context = {}
        today = time.strftime('%Y-%m-%d %H:%M:%S')
        if ids:
            ids = ids
        else:
            ids = self.search(cr, uid, [('next_invoice_date', '<', today),('expired', '=', False), ('state','=','active')])
        if ids:
            for id in ids:
                create_ids = []
                contract_obj = self.browse(cr,uid,id,context=None)
                obj_lines = self.pool.get('account.invoice.line')
                inv_obj = self.pool.get('account.invoice')
                line_id = obj_lines.create(cr, uid, {
                            'name': contract_obj.product_id.name,
                            'origin' : contract_obj.sale_order_id.name,
                            'price_unit': contract_obj.product_id.list_price,
                            'quantity': 1,
                            'product_id': contract_obj.product_id.id,
                            'account_id': contract_obj.partner_id.property_account_receivable.id,
                        })
                create_ids.append(line_id)
                orgin = str(contract_obj.sale_order_id.name)+' '+str(contract_obj.name)
                if contract_obj.partner_id and contract_obj.partner_id.property_payment_term.id:
                    pay_term = contract_obj.partner_id.property_payment_term.id
                else:
                    pay_term = False
                inv = {
                            'name': contract_obj.name,
                            'origin': orgin,
                            'type': 'out_invoice',
                            'account_id': contract_obj.partner_id.property_account_receivable.id,
                            'reference': "P%dC%dSO%d" % (contract_obj.partner_id.id,contract_obj.contract_type_id.id, contract_obj.sale_order_id.id),
                            'partner_id': contract_obj.partner_id.id,
                            'payment_term': pay_term,
                            'address_invoice_id': contract_obj.sale_order_id.partner_invoice_id.id,
                            'address_contact_id': contract_obj.sale_order_id.partner_order_id.id,
                            'invoice_line': [(6, 0, create_ids)],
                            'currency_id': contract_obj.sale_order_id.pricelist_id.currency_id.id,
                            'comment': contract_obj.sale_order_id.note,
                            'contract_id' : id
                        }
                inv_id = inv_obj.create(cr, uid, inv)
                invoice_interval_qty = contract_obj.invoice_qty
                invoice_interval_unit = contract_obj.invoice_intervel_unit
                if contract_obj.next_invoice_date:
                    invoice_date = contract_obj.next_invoice_date
                else:
                    invoice_date = today
                cur_invoice_date = datetime.strptime(str(invoice_date),"%Y-%m-%d %H:%M:%S")
                if invoice_interval_unit == 'months':
                    next_invoice_date = (cur_invoice_date + relativedelta(months=invoice_interval_qty))
                elif invoice_interval_unit == 'days':
                    next_invoice_date = (cur_invoice_date + relativedelta(days=invoice_interval_qty))
                elif invoice_interval_unit == 'weeks':
                    next_invoice_date = (cur_invoice_date + relativedelta(weeks=invoice_interval_qty))
                self.write(cr,uid,ids,{'next_invoice_date' : next_invoice_date},context=None)
            return True
contract()

class invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
                'contract_id' : fields.many2one('sale.contract','Contract Id')
                }
invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: