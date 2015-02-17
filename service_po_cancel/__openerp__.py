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
    'name': 'Module to cancel done purchase order',
    'version': '1.00',
    'category': 'Purchase Management',
    'description': """ 
        Module to cancel done purchase order
    """,
    'author': 'SF Soluciones',
    'website': 'sfsoluciones.com',
    'depends': ['account_cancel', 'purchase'],
    'init_xml': [],
    'update_xml': [
                   'purchase_view.xml',
                   'security/purchase_security.xml'
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: