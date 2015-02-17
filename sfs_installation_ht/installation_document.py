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
from tools.translate import _

class install_brand(osv.osv):
    _name = "install.brand"
    _description = "Brand of the device part"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code',size=32),
        'note': fields.text('Notes')
        }
install_brand()

class install_model(osv.osv):
    _name="install.model"
    _description = "Model of the device part"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code',size=32),
        'note': fields.text('Notes')
        }
install_model()

class install_brake_type(osv.osv):
    _name = "install.brake.type"
    _description = "Brake types used in a vehicle"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code',size=32),
        'note': fields.text('Notes')
        }
install_brake_type()

class install_transmission(osv.osv):
    _name = "install.transmission"
    _description = "Transmission method used in a vehicle"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code',size=32),
        'note': fields.text('Notes')
        }
install_transmission()

class install_retarder(osv.osv):
    _name = "install.retarder"
    _description = "Retarder used for the vehicle"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code',size=32),
        'note': fields.text('Notes')
        }
install_retarder()

class installation_document(osv.osv):
    _name = "install.doc"
    _columns = {
        'name': fields.char('Installation Number',size=64, required=True),
        'origin': fields.char('Source Document', size=64,),
        'picking_id': fields.many2one('stock.picking','Delivery Order', domain="[('type','=','out')]"),
        'sale_id':fields.many2one('sale.order','Sale Order',readonly=True),
        'planned_date': fields.date('Planned Date',readonly=True),
        'start_date': fields.date('Start'),
        'end_date': fields.date('End'),
        'partner_id':fields.many2one('res.partner','Customer'),
        'phone':fields.char('Telephone',size=16),##need verification
        'address_id':fields.many2one('res.partner.address','Customer Address'),
        'latitude': fields.integer('Latitude'),# 8 decimal numeric field
        'length': fields.integer('Length'),# 8 decimal numeric field
        'user_id': fields.many2one('res.users','Installed User'),#state
        'is_install': fields.boolean('In Installation Process', readonly=True),
        'is_uninstall': fields.boolean('In Uninstallation Process', readony=True),
        'install_line_ids':fields.one2many('install.doc.line','install_id','Installation Lines'),
        'state': fields.selection([
            ('draft','Ready'),
            ('progress','In Progress'),
            ('done','Done'),
            ('uninstall','In Uninstallation'),
            ('finish','Finish')],'State',
            help="* Ready: when triggered, it is the initial state\n"\
                 "* In Progress: when devices installed partially\n"\
                 "* In Uninstallation: when devices are being uninstalled\n"\
                 "* Done: when they are finished installing all devices\n"\
                 "* Finish: when it is finished doing all the uninstall\n",readonly=True),
        'contact_name': fields.char('Contact Name',size=32),
        'mobile': fields.char('Cell Phone',size=16),
        'email': fields.char('Email', size=64),
        }

    def onchange_partnerid(self, cr, uid, ids, partner_id, context=None):
        res = {}
        if partner_id:
            address = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery'])
            del_address = address['delivery']
            res['address_id'] = del_address
        return {'value': res}
            
    def create(self, cr, uid, vals, context=None):
        if not vals.get('picking_id', False):
            raise osv.except_osv(_("Error"), _("You are trying to create a record " \
                                               "that doesn't have a related picking"))
        return super(installation_document, self).create(cr, uid, vals, context=context)

    def start_install(self, cr, uid, ids, context=None):

        return True

    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'install.doc'),
        'state': 'draft'
        }
installation_document()

class installation_document_line(osv.osv):
    _name = "install.doc.line"
    _columns = {
        'name': fields.char('Device Name',size=128,required=True),
        'product_id': fields.many2one('product.product','Product'),
        'install_id': fields.many2one('install.doc','installation Document', ondelete='cascade'),
        'prodlot_id': fields.many2one('stock.production.lot','Control Serial Number'),
        'location_id': fields.many2one('stock.location','Location',domain="[('usage','=','internal')]"),
        'qty': fields.float('Quantity',digits=(16,3),),
        'uom_id': fields.many2one('product.uom','UOM'),
        'move_id': fields.many2one('stock.move','Stock Move'),
        'engine_serial_no': fields.char('Engine Serial Number', size=16,
                                        help="Engine serial number of the vehicle"\
                                        " in which the equipment is installed"),
        'economic_no': fields.char("Economic number", size=16,
                                   help="Economic number of the vehicle"),
        'license_plate': fields.char("License plates", size=32),
        'brand_id': fields.many2one('install.brand','Brand',),#may be many2one
        'engine_brand_id': fields.many2one('install.brand','Engine Brand',),#may be many2one
        'model_id': fields.many2one('install.model','Model'),#may be many2one
        'engine_model_id': fields.many2one('install.model','Engine Model',),#may be many2one
        'year': fields.char('Year', size=4),
        'brake_type_id': fields.many2one('install.brake.type','Brake Type'),#may be many2one
        'transmission_id': fields.many2one('install.transmission','Transmission'),#may be many2one
        'retarder_id': fields.many2one('install.retarder','Retarder',),#may be many2one
        'speed_limit': fields.integer('Speed Limit'),
        'max_time': fields.integer('Maximum time authorized stop',help='Maximum time authorized stop (Minutes)'),
        'note': fields.text('Notes'),
        'state': fields.selection([('draft','Ready'),
                                   ('installed','Installed'),
                                   ('uninstalled','Uninstalled')],'State',readonly=True),
        'saved': fields.boolean('Saved',help="This is for internal use only")
        }

    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False,
                        loc_id=False, product_id=False, uom_id=False, context=None):
        res = self.pool.get('stock.move').onchange_lot_id(cr, uid,[],prodlot_id,product_qty,
                                                          loc_id,product_id,uom_id,context)
        if prodlot_id:
            if isinstance(prodlot_id, tuple):
                prodlot_id = prodlot_id[0]
            prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, context=context)
            name = self.pool.get('product.product').name_get(cr, uid, [prodlot.product_id.id], context)[0][1]
            res['value'] = {'name': name, 'product_id': prodlot.product_id.id}
        return res

    def start_install(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{'state': 'installed'})
        return True

    def start_uninstall(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{'state': 'uninstalled'})
        return True

    _defaults = {
        'state': 'draft',
        'saved': False
        }

installation_document_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: