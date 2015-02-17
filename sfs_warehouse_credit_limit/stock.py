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
import netsvc
from osv import fields, osv
from mx import DateTime
from tools import config
from tools.translate import _

def check_limit(self, cr, uid, ids,sale_obj, context={}):
        partner = self.pool.get('res.partner').browse(cr, uid, ids[0], context)


        moveline_obj = self.pool.get('account.move.line')
        movelines = moveline_obj.search(cr, uid, [('partner_id', '=', partner.id),('account_id.type', 'in', ['receivable', 'payable']), ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(cr, uid, movelines)

        debit, credit = 0.0, 0.0
        for line in movelines:
            if line.date_maturity < time.strftime('%Y-%m-%d'):
                credit += line.debit
                debit += line.credit

        total=credit - debit
        if sale_obj :
            total+= sale_obj.amount_total
        if (total) > partner.credit_limit:
            msg = 'Cannot process Delivery Order, as it exceeds partner credit limits! \n Total Amount due as on %s is %s \n Check Partner Accounts or Credit Limits !' % (time.strftime('%Y-%m-%d'),total)
#            print'msg',msg
#            raise osv.except_osv(_('Credit Over Limits !'), _(msg))
            return {'status': False,'msg': msg}

        else:
            return True
class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def action_process(self, cr, uid, ids, context=None):
        for rec in self.browse(cr,uid,ids):
            if rec.type=='out' and rec.address_id and rec.address_id.partner_id :
                check_limit_status= check_limit(self, cr, uid, [rec.address_id.partner_id.id],rec.sale_id, context={})
                if check_limit_status and  type(check_limit_status) == dict and 'status' in check_limit_status and  not check_limit_status['status'] :
                    #msg = 'Can not confirm Slae Order, Total mature due Amount %s as on %s !\nCheck Partner Accounts or Credit Limits !' % (credit - debit, time.strftime('%Y-%m-%d'))
                    raise osv.except_osv(_('Credit Over Limits !'), _(check_limit_status['msg']))
        return super(stock_picking, self).action_process(cr, uid, ids, context)
stock_picking()

class stock_move(osv.osv):
    _inherit = "stock.move"

    def action_partial_move(self, cr, uid, ids, context=None):
        for rec in self.browse(cr,uid,ids):
            if rec.picking_id and rec.picking_id.type == 'out' and rec.picking_id.address_id and rec.picking_id.address_id.partner_id  :
                check_limit_status= check_limit(self, cr, uid, [rec.picking_id.address_id.partner_id.id], context={})
                if check_limit_status and  type(check_limit_status) == dict and 'status' in check_limit_status and  not check_limit_status['status'] :
                    #msg = 'Can not confirm Slae Order, Total mature due Amount %s as on %s !\nCheck Partner Accounts or Credit Limits !' % (credit - debit, time.strftime('%Y-%m-%d'))
                    raise osv.except_osv(_('Credit Over Limits !'), _(check_limit_status['msg']))
        return super(stock_move, self).action_partial_move(cr, uid, ids, context)
stock_move()