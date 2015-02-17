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
#
##############################################################################

{
    'name': 'Service Management - Contracts',
    'version': '0.18.3',
    'category': 'Generic Modules/Others',
    'description': """
    Module to create contracts.

    """,
    'author': 'SF Soluciones',
    'website': 'sfsoluciones.com',
    'depends': ['sale_layout','report_webkit','sfs_reference_calculation'],
    'init_xml': [],
    'update_xml': ['security/contract_security.xml',
                   'security/ir.model.access.csv',
                   'wizard/contract_invoice_view.xml',
                   'report_webkit_headers.xml',
                   'contract_data.xml',
                   'contract_view.xml',
                   'sale_view.xml',
                   'sale_layout_view.xml',
                   'contract_report.xml',
                   'partner_view.xml',
                   'agreement_template_view.xml',
    ],
    'demo_xml': [],
    'test': [ ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
