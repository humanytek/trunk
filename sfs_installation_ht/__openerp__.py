# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 ZestyBeanz Technologies Pvt. Ltd.
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
    "name" : "Installation Document",
    "version" : "0.2.2",
    "depends" : ['sale','sfs_serial_multy_number'],
    "author" : "SF Soluciones",
    'category' : 'Generic Modules/Others',
    "description": """To keep track of each devices installations made in
the locations of each customer and may keep the data to a precise control of each device installation.
    """,
    'website': 'sfsoluciones.com',
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'installation_document_sequence.xml',
        'installation_document_view.xml',
        'stock_view.xml',
        'sale_view.xml'
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
