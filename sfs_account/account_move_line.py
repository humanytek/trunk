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
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _


class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result
    _columns = {
                'journal_id': fields.related('move_id', 'journal_id', string='Journal', type='many2one', relation='account.journal', required=True, select=True, readonly=True,
                                store = {
                                    'account.move': (_get_move_lines, ['journal_id'], 20)
                                }),
        'period_id': fields.related('move_id', 'period_id', string='Period', type='many2one', relation='account.period', required=True, select=True, readonly=True,
                                store = {
                                    'account.move': (_get_move_lines, ['period_id'], 20)
                                }),
                }



account_move_line()

class account_move(osv.osv):
    _inherit = "account.move"
    def _check_centralisation(self, cursor, user, ids, context=None):
        for move in self.browse(cursor, user, ids, context=context):
            if move.journal_id.centralisation:
                move_ids = self.search(cursor, user, [
                    ('period_id', '=', move.period_id.id),
                    ('journal_id', '=', move.journal_id.id),
                    ])
                if len(move_ids) > 1:
                    return False
        return True

    def _check_period_journal(self, cursor, user, ids, context=None):
#        for move in self.browse(cursor, user, ids, context=context):
#            for line in move.line_id:
#                if line.period_id.id != move.period_id.id:
#                    return False
#                if line.journal_id.id != move.journal_id.id:
#                    return False
        return True

    _constraints = [
        (_check_centralisation,
            'You cannot create more than one move per period on centralized journal',
            ['journal_id']),
        (_check_period_journal,
            'You cannot create entries on different periods/journals in the same move',
            ['line_id']),
    ]


account_move()