# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 ZestyBeanz Technologies Pvt. Ltd.
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

from osv import osv

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
                          name='', partner_id=False, lang=False, update_tax=True, date_order=False,
                          packaging=False, fiscal_position=False, flag=False, context=None):
        pricelist_pool = self.pool.get('product.pricelist')
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
                                                             uom=uom, qty_uos=qty_uos, uos=uos,
                                                             name=name, partner_id=partner_id, lang=lang,
                                                             update_tax=update_tax, date_order=date_order,
                                                             packaging=packaging, fiscal_position=fiscal_position,
                                                             flag=flag, context=context)
        if product and pricelist:
            pricelist_obj = pricelist_pool.browse(cr, uid, pricelist, context=context)
            price = pricelist_pool.price_get(cr, uid, [pricelist], product, qty or 1.0, partner_id,
                                             {
                                             'uom': uom or result.get('product_uom'),
                                             'date': date_order,
                                             'pricelist_curr_id': pricelist_obj.currency_id.id,
                                             })[pricelist]
            if price is False:
                    warn_msg = _("Couldn't find a pricelist line matching this product and quantity.\n"
                                 "You have to change either the product, the quantity or the pricelist.")

                    warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                    res['value'].update({'price_unit': price})
        return res
    
sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: