# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class device_commission_wizard(osv.osv_memory):
    _name = "device.commission.wizard"
    _description = "Device Commission"
    _columns = {
        'emp_id': fields.many2one('hr.employee', 'Employee'),
        'initial_date': fields.date("Initial Date"),
        'end_date': fields.date("End Date")
        }
    
    def print_report(self, cr, uid, ids, context=None): 
        emp_id = False
        initial_date = False
        end_date = False       
        for object in self.browse(cr, uid, ids, context=context):
            emp_id = object.emp_id
            initial_date = object.initial_date
            end_date = object.end_date
        active_ids = context.get('active_ids',False)
        service_obj = self.pool.get('service.order.line')
        service_ids = []  
        if emp_id and initial_date and end_date:
            service_report_ids = self.pool.get('service.order.line.report').search(cr, uid, [
                              ('sr_installator_id', '=', emp_id.id),
                              ('sr_inst_start_date', '>=', initial_date),
                              ('sr_inst_end_date', '<=', end_date)])
#            if service_report_ids:
#                service_ids = service_obj.search(cr, uid, [
#                              ('installator_id', '=', emp_id.id),
#                              ('service_order_line_report_ids', '=', service_report_ids)])
            if service_report_ids:
                return {
                    'type'         : 'ir.actions.report.xml',
                    'report_name'  : 'device.commission',
                    'datas'        : {
                            'model':'service.order.line.report',
                            'id':   service_report_ids and service_report_ids[0] or False,
                            'ids':  service_report_ids or [],
                            'initial_date': initial_date,
                            'end_date': end_date
                                },
                    'nodestroy': False
                    }
        return True            
    
device_commission_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: