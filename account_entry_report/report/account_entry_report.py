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

import time
import pooler
from report import report_sxw

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'show_credit': self._show_total_credit,
            'show_debit': self._show_debit,
        })
    
    def _show_total_credit(self, oid):
         cr = self.cr
         rec = pooler.get_pool(self.cr.dbname).get('account.move').browse(cr, self.uid, oid)
         total_credit = 0.00
         for line in rec.line_id:
             total_credit = total_credit+line.credit
         return total_credit
     
    def _show_debit(self, oid):
         cr = self.cr
         rec = pooler.get_pool(self.cr.dbname).get('account.move').browse(cr, self.uid, oid)
         total_debit = 0.00
         for line in rec.line_id:
             total_debit = total_debit+line.debit
         return total_debit
     
report_sxw.report_sxw('report.account.move.report', 'account.move', 'addons/account_entry_report/report/account_entries.rml', parser=order, header="internal landscape")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: