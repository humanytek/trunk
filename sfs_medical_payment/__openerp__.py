# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2011 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
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
    "name" : "Medical Insurance Systems for sfsoluciones.com",
    "version" : "0.2",
    "depends" : ["medical_inpatient"],
    "author" : "Zesty Beanz Technologies",
    'category' : 'Generic Modules/Others',
    "description": """To manage the daily activities of the hospital its proposed to use an Enterprise Resource Planning application
    which will play a key role in the succesful execution of the
    Hospital Departamental Universitario Del Quindio San Juan De Dios visions and growth
    """,
    'website': 'http://sfsoluciones.com',
    'init_xml': [],
    'update_xml': ['wizard/pharmacy_payment_view.xml',
                   'wizard/stock_return_picking_view.xml',
                   'pharmacy_menu.xml','pharmacy_view.xml',
                   'medical_view.xml',
                   'medical_order_view.xml',
                   'account_statement_view.xml',
                  # 'pharmacy_src_view.xml'


                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: