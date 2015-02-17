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
from osv import fields, osv
from tools.translate import _
from tools import float_compare

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)      
        if uom:
            uom2 = self.pool.get('product.uom').browse(cr, uid, uom)                  
        if product:
            warning_msgs = ''
            product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
            uom3 = product_obj.uom_id
            if not uom2:
                uom2 = product_obj.uom_id
            compare_qty = float_compare((product_obj.qty_available - abs(product_obj.outgoing_qty)) * uom2.factor, qty * product_obj.uom_id.factor, precision_rounding=product_obj.uom_id.rounding)
            compare_qty2 = float_compare(product_obj.virtual_available * uom2.factor, qty * product_obj.uom_id.factor, precision_rounding=product_obj.uom_id.rounding)
            if (product_obj.type == 'product') and int(compare_qty) == -1 \
              and (product_obj.procure_method == 'make_to_stock'):
                warn_msg = _('You plan to sell %.2f %s but you only have %.2f %s available !\nThe real stock is %.2f %s. \n and %.2f %s are reserved') % \
                        (qty, uom3 and uom3.name or product_obj.uom_id.name,
                         max(0,product_obj.qty_available), product_obj.uom_id.name,
                         max(0,product_obj.qty_available), product_obj.uom_id.name,
                         abs(product_obj.outgoing_qty) ,product_obj.uom_id.name)
                warning_msgs += _("Not enough stock ! : ") + warn_msg + "\n\n"
                res.update({'warning': {'message': warning_msgs}})
                if warning_msgs:
                    context.update({'warning_from_sale_order_line_active': True})
            elif (product_obj.type == 'product') and (int(compare_qty2) == 1 or int(compare_qty2) == 0) \
                   and (product_obj.procure_method == 'make_to_stock')  and int(qty) > 0:
                   res.update({'warning': {}})
        return res
    
    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, context=None):
        res = super(sale_order_line, self).product_uom_change(cursor, user, ids, pricelist, product, qty=qty,
                                                              uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                                                              lang=lang, update_tax=update_tax, date_order=date_order, context=context)
        if context.get('warning_from_sale_order_line_active', False):
            res.update({'warning': {}})
        return res
    
sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
