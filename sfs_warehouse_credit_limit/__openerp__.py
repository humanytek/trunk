# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2011 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    conatct@zbeanztech.com
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
    "name" : "Warehouse Partner Credit Limit",
    "version" : "0.2",
    "depends" : ["stock"],
    "author" : "Zesty Beanz Technologies",
    'category' : 'Generic Modules/Others',
    "description": """Partner Credit Limit'
    Checks for all over due payment and already paid amount
    if the differance is positive and acceptable then Warehouse user
    able to confirm delivery order.
    """,
    'website': 'http://www.zbeanztech.com',
    'init_xml': [],
    'update_xml': [],
    'demo_xml': [],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: