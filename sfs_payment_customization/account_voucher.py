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

import netsvc
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

class account_voucher(osv.osv):
    _inherit = "account.voucher"

    _columns = {
                'user_id' : fields.related('line_ids','move_line_id', 'invoice','user_id',
                    type='many2one', relation='res.users',string='Salesman'),
                }
account_voucher()
