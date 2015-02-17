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

{
    'name': 'Vie Vert Invoice Customization',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """This module adds a phrase in the company which will be displayed in the invoice printed""",
    'author': 'SF Soluciones',
    'website': 'sfsoluciones.com',
    'images': [],
    'depends': ['account', 'l10n_mx_facturae_cbb'],
    'init_xml': [],
    'update_xml': [
                   'res_company_view.xml',
                   'invoice_report.xml'
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
