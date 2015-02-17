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
from sfs_service_order_csv_import.wizard import data_import

class import_log(osv.osv):
    
    _order = 'create_date desc'
    _name='import.log'
    _columns = {
        'create_date': fields.datetime('Created Date', readonly=True),
        'summary': fields.text('Summary', readonly=True),
#        'model_id': fields.many2one('ir.model', 'Model', readonly=True),
        'model': fields.selection(data_import._get_models, 'Model', readonly=True),
        'csv_file': fields.binary('Imported File', readonly=True),
        }
import_log()
