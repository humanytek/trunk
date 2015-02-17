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
from osv import osv, fields

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'install_doc_ids': fields.one2many('install.doc', 'sale_id', 'Related Installation Document',
                                           readonly=True, help="This is a list of installation documents that has been generated for this sales order."),
        }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'install_doc_ids':[],
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)

sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: