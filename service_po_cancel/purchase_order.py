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

from osv import osv, fields

from tools.translate import _

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def _get_product_type(self, cr, uid, ids, name, args, context=None):
        res = {}
        for purchase_obj in self.browse(cr, uid, ids, context=context):
            is_service = True
            for purchase_line_obj in purchase_obj.order_line:
                if purchase_line_obj.product_id.type != 'service':
                    is_service = False
            res[purchase_obj.id] = is_service
        return res
    
    _columns = {
                'is_service_purchase': fields.function(_get_product_type, type='boolean', string="Is Service?")
                }
    
    def done_purchase_cancel(self, cr, uid, ids, context=None):
        for purchase_obj in self.browse(cr, uid, ids, context=context):
            if purchase_obj.invoice_ids:
                raise osv.except_osv(_("Warning !"), _("This purchase order has associated invoices. Delete them first."))
            else:
                self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        for purchase_obj in self.browse(cr, uid, ids, context=context):
            if purchase_obj.is_service_purchase:
                self.write(cr, uid, ids, {'invoice_method': 'order'}, context=context)
        res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
        return res
    
purchase_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: