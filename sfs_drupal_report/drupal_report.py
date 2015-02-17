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
##
##############################################################################
import time
from lxml import etree
import xmlrpclib
import netsvc
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
import base64
import os

class sale_order(osv.osv):
    _inherit = "sale.order"



    def report_print(self, cr, uid, report, id):

        service = netsvc.LocalService(report)
        (result, format) = service.create(cr, uid, [id], {}, {})

        if not os.path.exists("/tmp/%s/"%cr.dbname):
            os.makedirs("/tmp/%s/"%cr.dbname)
        report_file = '/tmp/'+cr.dbname+'/reports'+ str(id) + '.pdf'
        fp = open(report_file,'wb+')
        fp.write(result);
        fp.close();
        return report_file

    def report_call(self, cr, uid, ids,context={}):

        if 'report_name' in context:
            report=context['report_name']
        else:
            report='report.sale.order'

        #print base64.b64encode(file(self.report_print(cr, uid, report,ids[0])).read())
        return base64.b64encode(file(self.report_print(cr, uid, report,ids[0])).read())


sale_order()

class account_invoice(osv.osv):
    _inherit = "account.invoice"



    def report_print_invoice(self, cr, uid, report, id):

        service = netsvc.LocalService(report)
        (result, format) = service.create(cr, uid, [id], {}, {})

        if not os.path.exists("/tmp/%s/"%cr.dbname):
            os.makedirs("/tmp/%s/"%cr.dbname)
        report_file = '/tmp/'+cr.dbname+'/reports'+ str(id) + '.pdf'

        fp = open(report_file,'wb+')
        fp.write(result);
        fp.close();
        return report_file

    def report_call_invoice(self, cr, uid, ids,context={}):

        if 'report_name' in context:
            report=context['report_name']
        else:
            report='report.account.invoice'


        return base64.b64encode(file(self.report_print_invoice(cr, uid, report,ids[0])).read())


account_invoice()