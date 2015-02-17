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
import tools
from osv import fields, osv

class service_report(osv.osv):
    _name = "service.report"
    _description = "Service Orders Statistics"
    _auto = False
    _rec_name = 'date'
    _columns = {
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'customer_device_id': fields.many2one('sale.order', 'Customer (device)'), 
        'date': fields.date('Date'), 
        'real_install_date': fields.datetime('Dates (real of installation)'),
        'order_state': fields.selection([('pending', 'Pending'),
                                   ('inst_asig', 'Installer Assigned'),
                                   ('in_process', 'In Process'),
                                   ('act_pend', 'Activation Pending'),
                                   ('done', 'Done'),
                                   ('cancelled', 'Cancelled')], 'State of service order'),   
        'order_line_state': fields.selection([('test', 'Test'), ('sale', 'Sale'),
                                            ('rent', 'Rent')], 'State of device'),
#        'order_line_state': fields.selection([('pending', 'Pending'),
#                                   ('done', 'Done')], 'State of device order line'),
        'service': fields.selection([('installation', 'Installation'),
                                   ('revision', 'Revision'),
                                   ('uninstall', 'Uninstall'),
                                   ('reinstall', 'Reinstall')], 'Service'),  
        'economic_num': fields.char('Economic number', size=64),
        'sim_card_number': fields.char('Sim card (number)', size=64),    
        'installator_id': fields.many2one('hr.employee', 'Installator person'),
        'sale_order_id': fields.many2one('sale.order', 'Sale Order'),
        'service_order': fields.char('Service order', size=64), 
        'problem_id': fields.many2one('service.problem', 'Problem'),
#        'contract_seq': fields.char('Contract sequence', size=64), 
        'sales_man_id': fields.many2one('res.users', 'Salesman'),
        'lot': fields.char('Lot', size=64), 
#        'contract_expire_date_': fields.date('Date of expire contract')
    }
    _order = 'date desc'
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'service_report')
        cr.execute("""
                           create or replace view service_report as (
               select
                    lr.id as id,
                    s.customer_id,
                    s.sale_order_id as customer_device_id,
                    s.proposed_date_ as date,
                    lr.sr_inst_end_date as real_install_date,
                    s.state as order_state,
                    s.product_state as order_line_state,
                    lr.sr_service_type as service,
                    l.economic_num,
                    l.installator_id,
                    s.sale_order_id,
                    s.name as service_order,
                    l.problem_id,
                    so.user_id as sales_man_id,
                    l.serial_number as lot,
                    slc.control_number as sim_card_number
                from
                   service_order_line_report lr
                   join service_order_line l on (l.id=lr.service_order_line_id)
                   join service_order s on (s.id=l.service_order_id)
                   join sale_order so on (so.id=s.sale_order_id)
                   join sale_order_line sol on (sol.order_id=so.id and sol.product_id = l.kit_id)
                   left join stock_production_lot spl on (l.kit_id = spl.product_id)
                   left join stock_lot_control slc on (spl.id = slc.prodlot_id)
                   left join stock_lot_config slcon on (slc.lot_config_id = slcon.id)
                where slcon.name LIKE '%SIM%' 
                group by
                    lr.id,
                    s.customer_id,
                    s.sale_order_id,
                    s.proposed_date_,
                    lr.sr_inst_end_date,
                    s.state,
                    s.product_state,
                    lr.sr_service_type,
                    l.economic_num,
                    s.phone,
                    l.installator_id,
                    s.sale_order_id,
                    s.name,
                    l.problem_id,
                    so.user_id,
                    l.serial_number,
                    slc.control_number
             ORDER BY lr.id ASC
            )
        """)
service_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: