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


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res= super(stock_picking, self).action_invoice_create(cr, uid, ids,journal_id=journal_id,group=group, type=type, context=context)
        for pick_id in res :
            pick_obj=self.browse(cr,uid,pick_id)
            invoice_obj=self.pool.get('account.invoice').browse(cr,uid,res[pick_id])
            if pick_obj.sale_id :
                user_id=False
                if pick_obj.sale_id.user_id :
                    user_id=pick_obj.sale_id.user_id.id
                self.pool.get('account.invoice').write(cr,uid,res[pick_id],{'user_id':user_id})
        return res

stock_picking()