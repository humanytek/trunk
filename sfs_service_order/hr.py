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
import decimal_precision as dp

class device_commision(osv.osv):
    _name = "device.commision"
    _description = "Device Commision"
    _columns = {
        'name': fields.many2one('product.product', 'Device'),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Sale Price')),
        'emp_id': fields.many2one('hr.employee', 'Employee'),
    }

device_commision()

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _description = "Employee"
    _columns = {
        'device_ids': fields.one2many('device.commision', 'emp_id', 'Device Commision')
    }

hr_employee()