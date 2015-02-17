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

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'install_doc': fields.boolean('Created Installation Document'),

        }
    _defaults = {
        'install_doc': False,
        }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'install_doc':False})
        return super(stock_picking, self).copy(cr, uid, id, default, context)

    def create_install_doc(self, cr, uid, ids, context=None):
        install_doc = self.pool.get('install.doc')
        install_line = self.pool.get('install.doc.line')
        for obj in self.browse(cr, uid, ids, context):
            install_id = install_doc.create(cr, uid, {
                'origin': obj.name,
                'picking_id': obj.id,
                'partner_id': obj.address_id and obj.address_id.partner_id \
                    and obj.address_id.partner_id.id or False,
                'contact_name': obj.address_id and obj.address_id.name,
                'phone': obj.address_id and obj.address_id.phone,
                'mobile': obj.address_id and obj.address_id.mobile,
                'email': obj.address_id and obj.address_id.email,
                'address_id': obj.address_id and obj.address_id.id or False,
                'user_id': uid,
                'sale_id': obj.sale_id.id
                }, context)
            for line in obj.move_lines:
                prod_name = self.pool.get('product.product').name_get(cr, uid, [line.product_id.id], context)[0][1]
                install_line.create(cr, uid, {
                    'install_id': install_id,
                    'name': prod_name,
                    'product_id': line.product_id.id,
                    'prodlot_id': line.prodlot_id and line.prodlot_id.id or False,
                    'move_id': line.id,
                    'qty': line.product_qty,
                    'uom_id': line.product_uom.id,
                    'location_id': line.location_id.id,
                    #'engine_serial_no': '/',
                    #'economic_no': '/',
                    #'license_plate': '/',
                    'saved':True
                    }, context)
            self.write(cr, uid, [obj.id],{'install_doc':True})
        return True
stock_picking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: