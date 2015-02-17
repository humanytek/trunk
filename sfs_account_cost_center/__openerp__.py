# -*- encoding: utf-8 -*-
##############################################################################
#
#     Copyright (c) 2013 SF Soluciones.
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

{
    "name" : "SFS Account Cost Center",
    "version" : "1.4",
    'author': 'SF Soluciones',
    'website': 'sfsoluciones.com',
    "category" : "Generic Modules",
    "depends" : [
                 'account_financial_report',
                 'hesatec_mx_accounting_reports_v61',
                 'stock'
                ],
    "description": """
       Cost Center and Cost center report modification
    """,
    'init_xml': [],
    'update_xml': [
                  'stock_view.xml',
                  'account_cost_center_view.xml',
                  'account_move_view.xml',
                  'account_financial_report_view.xml',
                  'account_mx_report_def_view.xml',
                  'wizard/wizard_report_view.xml',
                  'report/account_financial_report_view.xml',
                  'security/ir.model.access.csv'
                  ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'complexity':'easy'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: