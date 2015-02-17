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

from osv import fields, osv
from tools.translate import _
class sale_order(osv.osv):
    _inherit = "sale.order"
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'approve_price': False,
            'not_require': False,
            })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)

    def not_require(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'not_require' :True})
        return True
    def approve_price(self, cr, uid, ids, context=None):
        for rec in self.browse(cr,uid,ids,context):
            product_details='Este pedido contiene precios no aprobados, por favor solicite la autorizacion de precios necesaria para continuar el proceso  \t  \n\n'
            flag=True
            for line in rec.order_line :
                if line.product_id and line.price_unit >= line.product_id.list_price :
                    product_details+=line.product_id.name +'\n'
                    flag=False
            if flag :
                    self.write(cr,uid,ids,{'approve_price' :True})
            else:
                raise osv.except_osv(
                        _('Prices can not be approved !'),
                        _(product_details))

        return True

    _columns = {
                'approve_price':fields.boolean('Precios Aprobados',readonly=True),
                'not_require':fields.boolean('Precios Aprobados',readonly=True),
                }
    _defaults = {
                 'approve_price': False,
                 }
sale_order()
