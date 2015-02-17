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

from sfs_product_catalog import JasperDataParser
from jasper_reports import jasper_report

class jasper_product_catlog(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_product_catlog, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'records'

    def generate_parameters(self, cr, uid, ids, data, context):
        return {}

    def generate_properties(self, cr, uid, ids, data, context):
        return {
                'net.sf.jasperreports.export.ignore.page.margins':'true',
                }

    def generate_records(self, cr, uid, ids, data, context):
        if context is None:
            context = {}
        result = []
        string = ""
        product_pool = self.pool.get('product.product')
        for product_obj in product_pool.browse(cr, uid, context.get('active_ids', []), context=context):
            data = {}
            product_code = product_obj.default_code
            product_name = product_obj.name and product_obj.name[0:60] or ''
            list_price = product_obj.list_price
            string = str(product_code) + "\t" + product_name + "\t" + str(list_price)
            data['line'] = string
            result.append(data)
        return result
    
jasper_report.report_jasper('report.product_catalog_report', 'product.product', 
                            parser=jasper_product_catlog, )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
