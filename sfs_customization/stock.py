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
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import logging

class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
#
#    def default_get(self, cr, uid, fields, context=None):
#        """ To get default values for the object.
#         @param self: The object pointer.
#         @param cr: A database cursor
#         @param uid: ID of the user currently logged in
#         @param fields: List of fields for which we want default values
#         @param context: A standard dictionary
#         @return: A dictionary which of fields with values.
#        """
#        if context is None:
#            context = {}
#
#        pick_obj = self.pool.get('stock.picking')
#        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
#        picking_ids = context.get('active_ids', [])
#        if not picking_ids:
#            return res
#
#        result = []
#        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
#            pick_type = self.get_picking_type(cr, uid, pick, context=context)
#            for m in pick.move_lines:
#                if m.state in ('done', 'cancel') or pick.type == 'internal' and m.state not in ('assigned'):
#                    continue
#                result.append(self.__create_partial_picking_memory(m, pick_type))
#
#        if 'product_moves_in' in fields:
#            res.update({'product_moves_in': result})
#        if 'product_moves_out' in fields:
#            res.update({'product_moves_out': result})
#        if 'date' in fields:
#            res.update({'date': time.strftime('%Y-%m-%d %H:%M:%S')})
#        return res
    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        pick_obj = self.pool.get('stock.picking')
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        for pick in pick_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            for m in pick.move_lines:
                if m.state in ('done', 'cancel') or pick.type == 'internal' and m.state not in ('assigned'):
                    list_index = 0
                    for item in res['product_moves_in']:
                        if item['move_id'] == m.id:
                            res['product_moves_in'].pop(list_index)

                        list_index += 1
        return res
stock_partial_picking()


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res= super(stock_picking, self).action_invoice_create(cr, uid, ids,journal_id=False,group=False, type='out_invoice', context=None)
        for pick_id in res :
            pick_obj=self.browse(cr,uid,pick_id)
            invoice_obj=self.pool.get('account.invoice').browse(cr,uid,res[pick_id])
            if pick_obj.sale_id :
                user_id=False
                if pick_obj.sale_id.user_id :
                    user_id=pick_obj.sale_id.user_id.id
                self.pool.get('account.invoice').write(cr,uid,res[pick_id],{'user_id':user_id})
        return res
    def draft_validate(self, cr, uid, ids, context=None):
        """ Validates picking directly from draft state.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        move_obj = self.pool.get('stock.move')
        self.draft_force_assign(cr, uid, ids)
        for pick in self.browse(cr, uid, ids, context=context):
            move_ids = [x.id for x in pick.move_lines]
            if pick.type == 'internal' :
                self.action_assign(cr,uid,[pick.id])
            else:
                move_obj.force_assign(cr, uid, move_ids)
            wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
        return self.action_process(
            cr, uid, ids, context=context)
stock_picking()