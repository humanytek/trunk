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

class wizard_report(osv.osv_memory):
    _inherit = 'wizard.report'
    
    def onchange_afr_id(self, cr, uid, ids, afr_id, context=None):
        res = super(wizard_report, self).onchange_afr_id(cr, uid, ids, afr_id, context=context)
        if res.get('value', False) and afr_id:
            account_fin_report_obj = self.pool.get('afr').browse(cr, uid, afr_id, context=context)
            res['value'].update({'cost_center_ids': [cent.id for cent in account_fin_report_obj.cost_center_ids]})
        return res
    
    _columns = {
                'cost_center_ids': fields.many2many('account.cost.center', 'costcenter_wiz_rel', 'wizard_id',
                                                    'cost_center_id', 'Cost Center')
                }
    
    def print_report(self, cr, uid, ids, data, context=None):
        res = super(wizard_report, self).print_report(cr, uid, ids, data, context=context)
        data['form'] = self.read(cr, uid, ids[0])
        name = 'afr.1cols.inherit'
        if data['form']['columns'] == 'one':
            name = 'afr.1cols.inherit'
        if data['form']['columns'] == 'two':
            name = 'afr.2cols.inherit'
        if data['form']['columns'] == 'four':
            if data['form']['analytic_ledger'] and data['form']['inf_type'] == 'BS':
                name = 'afr.analytic.ledger.inherit'
            else:
                name = 'afr.4cols.inherit'
        if data['form']['columns'] == 'five':
            name = 'afr.5cols.inherit'
        if data['form']['columns'] == 'qtr':
            name = 'afr.qtrcols.inherit'
        if data['form']['columns'] == 'thirteen':
            name = 'afr.13cols.inherit'
        res['report_name'] = name
        return res
    
wizard_report()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
