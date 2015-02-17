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

{
    'name': 'Service Order',
    'version': '1.18',
    'category': 'Service Order',
    'complexity': "easy",
    'description': "Service order",
    'author': 'SF Soluciones',
    'website': 'http://www.sfsoluciones.com',
    'depends': ['nan_product_pack','hr','sfs_serial_multy_number','sfs_contract'],
    'init_xml': [],
    'update_xml': [
        'security/service_order_security.xml',
        'service_order_view.xml',
        'service_order_sequence.xml',
        'report/service_report_view.xml',
        'service_workflow.xml',
        'sale_view.xml',
        'service_order_line_report.xml',
        'hr_view.xml',
        'wizard/device_commission_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: