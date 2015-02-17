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

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
    _columns = {
                'create_move': fields.boolean('Create Move For Statement Line')
                }
    _defaults = {
                 'create_move': True
                 }
account_bank_statement_line()

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'
    
    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id,
                                 st_line_number, context=None):
        res = True
        account_bank_statement_line_pool = self.pool.get('account.bank.statement.line')
        if st_line_id:
            account_bank_statement_pool = self.pool.get('account.bank.statement.line')
            statement_obj = account_bank_statement_pool.browse(cr, uid, st_line_id, context=context)
            if statement_obj.create_move:
                res = super(account_bank_statement, self).create_move_from_st_line(cr, uid,st_line_id,
                                                                                   company_currency_id,
                                                                                   st_line_number,
                                                                                   context=context)
                account_bank_statement_pool.write(cr, uid, statement_obj.id, {'create_move': False}, context=context)
        return res
    
    def _get_statement(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.bank.statement.line').browse(cr, uid, ids, context=context):
            result[line.statement_id.id] = True
        return result.keys()
    
    def _end_balance(self, cursor, user, ids, name, attr, context=None):
        res_currency_obj = self.pool.get('res.currency')
        res_users_obj = self.pool.get('res.users')
        company_currency_id = res_users_obj.browse(cursor, user, user,
                context=context).company_id.currency_id.id
        res = super(account_bank_statement, self)._end_balance(cursor, user, ids, name, attr, context=context)
        for statement_obj in self.browse(cursor, user, ids, context=context):
            for line in statement_obj.move_line_ids:
                currency_id = statement_obj.currency.id
                if line.debit > 0:
                    if line.account_id.id == \
                            statement_obj.journal_id.default_debit_account_id.id:
                        res[statement_obj.id] -= res_currency_obj.compute(cursor,
                                user, company_currency_id, currency_id,
                                line.debit, context=context)
                else:
                    if line.account_id.id == \
                            statement_obj.journal_id.default_credit_account_id.id:
                        res[statement_obj.id] += res_currency_obj.compute(cursor,
                                user, company_currency_id, currency_id,
                                line.credit, context=context)
        return res
    
    _columns = {
                'balance_end': fields.function(_end_balance,
                                               store = {
                                                        'account.bank.statement': (lambda self, cr, uid, ids, c={}: ids, ['line_ids','move_line_ids'], 10),
                                                        'account.bank.statement.line': (_get_statement, ['amount'], 10),
                                                        },
                                                        string="Computed Balance", help='Balance as calculated based on Starting Balance and transaction lines'),
                }
    
account_bank_statement()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
