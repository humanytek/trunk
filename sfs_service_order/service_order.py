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

from osv import osv, fields 
import netsvc
from tools.translate import _

class engine_brand(osv.osv):
    _name = "engine.brand"
    _description = "Engine Brand"
    _columns = {
        'name': fields.char('Brand', size=64)
    }
engine_brand()

class engine_model(osv.osv):
    _name = "engine.model"
    _description = "Engine Brand"
    _columns = {
        'name': fields.char('Model', size=64),
        'brand_id': fields.many2one('engine.brand', 'Brand'),
    }
engine_model()

class vehicle_brand(osv.osv):
    _name = "vehicle.brand"
    _description = "Vehicle Brand"
    _columns = {
        'name': fields.char('Brand', size=64)
    }
vehicle_brand()

class vehicle_model(osv.osv):
    _name = "vehicle.model"
    _description = "Vehicle Brand"
    _columns = {
        'name': fields.char('Model', size=64),
        'brand_id': fields.many2one('vehicle.brand', 'Brand'),
    }
vehicle_model()

class vehicle_protocol(osv.osv):
    _name = "vehicle.protocol"
    _description = "Vehicle Protocol"
    _columns = {
        'name': fields.char('protocol', size=64)
    }
vehicle_protocol()

class vehicle_type(osv.osv):
    _name = "vehicle.type"
    _description = "Vehicle Type"
    _columns = {
        'name': fields.char('Type', size=64)
    }
vehicle_type()

class service_problem(osv.osv):
    _name = "service.problem"
    _description = "Service Problem"
    _columns = {
        'name': fields.char('Problem', size=64)
    }
service_problem()

class service_order(osv.osv):
    _name = "service.order"
    _description = "Service Order"
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'service.order')
        })
        return super(service_order, self).copy(cr, uid, id, default, context=context)
    
    _columns = {
        'name': fields.char('Sequence', size=64, required=True),
        'source': fields.char('Source (delivery order)', size=64),
        'source_id': fields.many2one('stock.picking', 'Source (delivery order)'),
        'customer_id': fields.many2one('res.partner', 'Customer', required=True),
        'phone': fields.char('Phone', size=64),
        'mobile': fields.char('Mobile Phone', size=64),
        'address_id': fields.many2one('res.partner.address', 'Address', required=True),
        'sale_order_id': fields.many2one('sale.order', 'Sale Order'),
        'proposed_date_': fields.date('Proposed Date'),
        'proposed_time_': fields.time('Proposed Time'),
        'contract_seq': fields.char('Contract Sequence', size=64),
        'validity': fields.char('Validity/Life', size=64),
        'order_line_ids': fields.one2many('service.order.line', 'service_order_id',
                                           'Devices of service order lines'),
        'product_state': fields.selection([('test', 'Test'), ('sale', 'Sale'),
                                            ('rent', 'Rent')], 'State Of Product'),
        'state': fields.selection([('pending', 'Draft'),
                                   ('inst_asigned', 'Installer Assigned'),
                                   ('in_process', 'In Process'),
                                   ('act_pending', 'Activation Pending'),
                                   ('done', 'Done'),
                                   ('cancelled', 'Cancelled')], 'State')
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'service.order'),
        'state': 'pending'
            }
    
    def onchange_customer(self, cr, uid, ids, customer_id):
        v = {}
        if customer_id:
            customer = self.pool.get('res.partner').browse(cr, uid, customer_id)
            v['phone'] = customer.phone
            v['mobile'] = customer.mobile
            if customer.address:
                v['address_id'] = customer.address[0].id
            else:
                v['address_id'] = False
        return {'value': v}
    
    def action_state_change(self, cr, uid, ids, state):
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state': state})
        return True
    
service_order()

class service_order_line(osv.osv):
    _name = "service.order.line"
    _description = "Service Order Line"
    _columns = {
        'name': fields.selection([('1', ' '),
                                  ('installation', 'Installation'),
                                   ('revision', 'Revision'),
                                   ('uninstall', 'Uninstall'),
                                   ('reinstall', 'Reinstall')], 'Service Type'),
        'accessories_ids': fields.many2many('product.product', 'accessories_rel',
                             'product_id', 'order_line_id', 'Accessories Install'), 
        'production_lot_ids': fields.many2many('stock.production.lot', 'production_lot_rel',
                             'lot_id', 'order_line_id', 'Product'), 
        'kit_id': fields.many2one('product.product', 'Kit Product'),      
        'serial_number': fields.char('Serial Number', size=64),  
        'sequence': fields.char('Sequence', size=64),  
        'economic_num': fields.char('Economic number', size=64),
        'plates': fields.char('Plates', size=64),
        'brand_id': fields.many2one('vehicle.brand','Brand'),
        'vehicle_type_id': fields.many2one('vehicle.type', 'Type of vehicle'),
        'engine_brand_id': fields.many2one('engine.brand', 'Brand'),
        'engine_model_id': fields.many2one('engine.model', 'Model'),
        'installator_id': fields.many2one('hr.employee', 'Installator  Person'),
        'installator_status': fields.boolean('Installator  Status'),
        'transport_method': fields.char('Transport method', size=64),
        'cust_entry_req': fields.char('Entry requirements with the customer', size=64),
        'service_address_id': fields.many2one('res.partner.address', 'Service Address'),
        'contact_person_id': fields.many2one('res.partner.address', 'Contact Person'),
        'phone': fields.char('Phone', size=64),
        'mobile': fields.char('Mobile Phone', size=64),
        'problem_id': fields.many2one('service.problem', 'Problem'),
        'no_ticket': fields.char('No Ticket', size=64),
        'note': fields.text('Note'),
        'service_order_id': fields.many2one('service.order', 'Service Order'),
        'customer_id': fields.related('service_order_id', 'customer_id', type='many2one', relation='res.partner', string='Customer', readonly=True),
        'service_order_line_report_ids': fields.one2many('service.order.line.report', 'service_order_line_id',
                                           'Service order line Report'),
        'service_order_line_request_ids': fields.one2many('service.order.line.request', 'service_order_line_id',
                                           'Service order line Request'),
        'is_incoming_shipment_generated': fields.boolean('is_incoming_shipment_generated'),        
        'state': fields.selection([('pending', 'Pending'),
                                   ('done', 'Done')], 'State')
        }
    
    _defaults = {
        'state': 'pending',
        'name': '1',
        'installator_status': False,
        'is_incoming_shipment_generated': False,
        'sequence': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'service.order.line'),
            }
    
    def _create_service_order_line_request(self, cr, uid, oder_line_id, service_type, context=None):
        if oder_line_id:
            obj_service_line = self.browse(cr, uid, oder_line_id)
            if obj_service_line:
                list_access_ids = []
                list_production_ids = []
                if obj_service_line.accessories_ids:
                    for obj_accss in obj_service_line.accessories_ids:
                        list_access_ids.append(obj_accss.id)
                if obj_service_line.production_lot_ids:
                    for obj_prod in obj_service_line.production_lot_ids:
                        list_production_ids.append(obj_prod.id)
                request_id = self.pool.get('service.order.line.request').create(cr, uid, {'name': service_type,
                                          'production_lot_ids': [(6, 0, list_production_ids)],
                                          'accessories_ids': [(6, 0, list_access_ids)],
                                          'kit_id': obj_service_line.kit_id.id,
                                         'serial_number': obj_service_line.serial_number,
#                                         'installator_id': obj_service_line.installator_id.id,
                                         'installator_status': obj_service_line.installator_status,
#                                         'transport_method': obj_service_line.transport_method,
#                                         'cust_entry_req': obj_service_line.cust_entry_req,
#                                         'service_address_id': obj_service_line.service_address_id.id,
#                                         'contact_person_id': obj_service_line.contact_person_id.id,
#                                         'phone': obj_service_line.phone,
#                                         'mobile': obj_service_line.mobile,
#                                         'problem_id': obj_service_line.problem_id.id,
#                                         'no_ticket': obj_service_line.no_ticket,
#                                         'note': obj_service_line.note,
                                         'service_order_id': obj_service_line.service_order_id.id,
                                         'customer_id': obj_service_line.customer_id.id,
                                         'economic_num': obj_service_line.economic_num,
                                         'plates': obj_service_line.plates,
                                         'brand_id': obj_service_line.brand_id.id,
                                         'vehicle_type_id': obj_service_line.vehicle_type_id.id,
                                         'engine_brand_id': obj_service_line.engine_brand_id.id,
                                         'engine_model_id': obj_service_line.engine_model_id.id,
                                         'service_order_line_id': obj_service_line.id}, context=context)
            return request_id
        return False 
    
    def change_service_type_installation(self, cr, uid, ids, context=None):
        if ids:
           
            request_id = self._create_service_order_line_request(cr, uid, ids[0], 'installation', context=context)
            if request_id:
               self.write(cr, uid, ids[0], {'name': 'installation'}) 
        return True
    
    def change_service_type_revision(self, cr, uid, ids, context=None):
        if ids:
            request_id = self._create_service_order_line_request(cr, uid, ids[0], 'revision', context=context)
            if request_id:
               self.write(cr, uid, ids[0], {'name': 'revision'}) 
        return True
    
    def change_service_type_uninstall(self, cr, uid, ids, context=None):
        if ids:
            request_id = self._create_service_order_line_request(cr, uid, ids[0], 'uninstall', context=context)
            if request_id:
               self.write(cr, uid, ids[0], {'name': 'uninstall'}) 
        return True
    
    def change_service_type_reinstall(self, cr, uid, ids, context=None):
        if ids:
            request_id = self._create_service_order_line_request(cr, uid, ids[0], 'reinstall', context=context)
            if request_id:
               self.write(cr, uid, ids[0], {'name': 'reinstall'}) 
        return True
    
    def onchange_contact_person(self, cr, uid, ids, contact_person_id):
        v = {}
        if contact_person_id:
            contact_person = self.pool.get('res.partner.address').browse(cr, uid, contact_person_id)
            v['phone'] = contact_person.phone
            v['mobile'] = contact_person.mobile
        return {'value': v}
    
    def _create_stock_move(self, cr, uid, obj_service_order_line, picking_id, context=None):
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        search_picking_ids = picking_obj.search(cr, uid, [
                              ('sale_id', '=', obj_service_order_line.service_order_id.sale_order_id.id)])
        objs_search_picking = picking_obj.browse(cr, uid, search_picking_ids)
        kit_move_id = False
        count_move = 0;
        if obj_service_order_line.kit_id and obj_service_order_line.kit_id.pack_line_ids:
            for obj_search_picking in objs_search_picking:
                if obj_search_picking.move_lines: 
                    for move in obj_search_picking.move_lines:
                        for products_pack in obj_service_order_line.kit_id.pack_line_ids:
                            if move.product_id == products_pack.product_id:
                                for obj_lot in obj_service_order_line.production_lot_ids:
                                    if move.prodlot_id.id == obj_lot.id:
                                        move_id = move_obj.create(cr, uid, {'product_id': products_pack.product_id.id, 
                                                'picking_id': picking_id,
                                                'name': 'SRO '+obj_service_order_line.service_order_id.name+
                                                        ': ['+products_pack.product_id.default_code+']'+
                                                         products_pack.product_id.name,
                                                'product_uom' : products_pack.product_id.uom_id.id,
                                                'location_id': move.location_dest_id.id,
                                                'location_dest_id': move.location_id.id,
                                                'prodlot_id': move.prodlot_id.id,
                                                'product_qty': products_pack.quantity },context=context)
                                        if move_id:
                                            count_move = count_move + 1
                            elif move.product_id == obj_service_order_line.kit_id and kit_move_id == False:
                                kit_move_id = move_obj.create(cr, uid, {'product_id': obj_service_order_line.kit_id.id, 
                                                'picking_id': picking_id,
                                                'name': 'SRO '+obj_service_order_line.service_order_id.name+
                                                        ': ['+obj_service_order_line.kit_id.default_code+']'+
                                                         obj_service_order_line.kit_id.name,
                                                'product_uom' : obj_service_order_line.kit_id.uom_id.id,
                                                'location_id': move.location_dest_id.id,
                                                'location_dest_id': move.location_id.id,
                                                'product_qty': 1 },context=context)
            if count_move > 0:
                count_packs = len(obj_service_order_line.kit_id.pack_line_ids)
                list_products = []
                if count_move < count_packs:
                    list_products.append(obj_service_order_line.kit_id)
                    for obj in obj_service_order_line.kit_id.pack_line_ids:
                        list_products.append(obj.product_id)
                    search_move_ids = move_obj.search(cr, uid, [
                              ('picking_id', '=', picking_id)])
                    if search_move_ids:
                        search_move_objs = move_obj.browse(cr, uid, search_move_ids)
                        for search_move_obj in search_move_objs:
                            list_products.remove(search_move_obj.product_id)
                    if  list_products:
                        for list_product in list_products:   
                            if objs_search_picking:
                                for  obj_search_picking in objs_search_picking:
                                    if obj_search_picking.move_lines: 
                                        for move in obj_search_picking.move_lines:
                                            if move.product_id == list_product:
                                                for products_pack in obj_service_order_line.kit_id.pack_line_ids:
                                                    if move.product_id == products_pack.product_id:
                                                        move_id = move_obj.create(cr, uid, {'product_id': products_pack.product_id.id, 
                                                                  'picking_id': picking_id,
                                                                  'name': 'SRO '+obj_service_order_line.service_order_id.name+
                                                                  ': ['+products_pack.product_id.default_code+']'+
                                                                  products_pack.product_id.name,
                                                                  'product_uom' : products_pack.product_id.uom_id.id,
                                                                  'location_id': move.location_dest_id.id,
                                                                  'location_dest_id': move.location_id.id,
                                                                  'prodlot_id': move.prodlot_id.id,
                                                                  'product_qty': products_pack.quantity },context=context)
                                               
        picking_data = picking_obj.browse(cr, uid, picking_id, context=context)
        state = picking_data.state
        move_id = False
        if picking_data.state != 'done':
                state = picking_data.state
            #while state != 'done':
                picking_data = picking_obj.browse(cr, uid, picking_id, context=context)
                if picking_data.move_lines:
                    for line in picking_data.move_lines:
                        move_id = move_obj.action_done(cr, uid, [line.id], context=context)
                state = picking_obj.browse(cr, uid, picking_id, context=context).state
        return True 
    
    def generate_incoming_shipment(self, cr, uid, ids, context=None):
        if ids:
            obj_service_order_line = self.browse(cr, uid, ids[0])
            picking_id = self.pool.get('stock.picking').create(cr, uid, {
                                        'origin': 'SRO '+obj_service_order_line.service_order_id.name, 
                                        'type': 'in',
                                        'address_id': obj_service_order_line.service_order_id.address_id.id 
                                        },context=context)
            if picking_id:
                self.write(cr,uid,ids,{ 'state': 'done', 'is_incoming_shipment_generated': True}, context=context)
                self._create_stock_move(cr, uid, obj_service_order_line, picking_id, context=None)
        return True
    
    def assign_installer(self, cr, uid, ids, context=None):
        if ids:
            order_line_objs = self.browse(cr, uid, ids)
            for order_line_obj in order_line_objs:
                if order_line_obj.installator_id:
                    self.write(cr, uid, order_line_obj.id, {'installator_status': True})
            
            order_line_objs = self.browse(cr, uid, ids)
            for order_line_obj in order_line_objs:
                if order_line_obj.installator_id:
                    self.write(cr, uid, order_line_obj.id, {'installator_status': True})        
                    if order_line_obj.service_order_id and order_line_obj.service_order_id.order_line_ids:
                        change_state = True
                        for obj in order_line_obj.service_order_id.order_line_ids:
                            if obj.installator_status == False:
                                change_state = False
                    if change_state == True:
                          wf_service = netsvc.LocalService("workflow")
                          self.pool.get('service.order').write(cr, uid, order_line_obj.service_order_id.id, {'state': 'inst_asigned'})
                          wf_service.trg_validate(uid, 'service.order', order_line_obj.service_order_id.id, 'installer_assigned', cr)      
        
        return True
    
    def oder_line_state_done(self, cr, uid, ids, context=None):
        if ids:
            self.write(cr, uid, ids[0], {'state': 'done'})
        return True
    
    def oder_line_state_reactivate(self, cr, uid, ids, context=None):
        if ids:
            self.write(cr, uid, ids[0], {'state': 'pending'})
        return True
      
service_order_line()

class service_order_line_report(osv.osv):
    
    def _get_sequence(self, cr, uid, ids, name, args, context=None):
        res = {}
        length = 1
        for order_line_report in self.browse(cr, uid, ids, context=context):
            if order_line_report.is_sequenced:
                res ={}
            else :
                for obj_order_line in order_line_report.service_order_line_id.service_order_line_report_ids:
                    if obj_order_line.is_sequenced:
                        length = length + 1
                self.write(cr, uid, order_line_report.id, {'is_sequenced': True})
                res[order_line_report.id] = order_line_report.service_order_line_id.sequence + '/' + str(length)
        return res
    
    _name = "service.order.line.report"
    _description = "Service Order Line Report"
    _rec_name = 'sequence'
    _columns = {
        #----------------Service Report------------------------------
        'is_sequenced': fields.boolean('Sequence'),
        'sequence': fields.function(_get_sequence, string='Sequence', readonly=True, type="char", method=True, size=64, store=True),
        'service_order_line_id': fields.many2one('service.order.line', 'Service Order Line'),
        'sr_inst_start_date': fields.datetime('Date start installation'),
        'sr_inst_end_date': fields.datetime('Date end installation'),
        'sr_installator_id': fields.many2one('hr.employee', 'Installator  Person'),
        'sr_service_type': fields.selection([('installation', 'Installation'),
                                   ('revision', 'Revision'),
                                   ('uninstall', 'Uninstall'),
                                   ('reinstall', 'Reinstall')], 'Type of Service'),
        'sr_contact_person_id': fields.many2one('res.partner.address', 'Contact  Person'),  
        'sr_service_address_id': fields.many2one('res.partner.address', 'Service Address'),    
        'sr_economic_num': fields.char('Economic number', size=64),
        'sr_type': fields.char('Type', size=64),
        'sr_brand_id': fields.many2one('vehicle.brand','Brand'),
        'sr_year': fields.char('Year', size=64),
        'sr_model_id': fields.many2one('vehicle.model','Model'),
        'sr_protocol_id': fields.many2one('vehicle.protocol','Protocol'),
        'sr_vehicle_type_id': fields.many2one('vehicle.type', 'Type of vehicle'),
        'sr_engine_brand_id': fields.many2one('engine.brand', 'Brand'),
        'sr_engine_model_id': fields.many2one('engine.model', 'Model'),   
        'sr_engine_serial_no': fields.char('Serial number', size=64),    
        'sr_production_lot_ids': fields.many2many('stock.production.lot', 'production_lot_rep',
                             'lot_id', 'order_line_id', 'Product'), 
        'sr_accessories_ids': fields.many2many('product.product', 'accessories_rep',
                                    'product_id', 'order_line_id', 'Accessories Install'), 
        'sr_problem_id': fields.many2one('service.problem', 'Problem'),
        'sr_solution': fields.text('Solution'),
        'sr_notes': fields.text('Notes'),
        'sr_amount': fields.float('Amount'),
        'state': fields.selection([('pending', 'Pending'),
                                   ('done', 'Done')], 'State')
        }
    
    _defaults = {
        'is_sequenced': False,
          }
     
service_order_line_report()

class service_order_line_request(osv.osv):
    
    def _get_sequence_request(self, cr, uid, ids, name, args, context=None):
        res = {}
        length = 1
        for order_line_request in self.browse(cr, uid, ids, context=context):
            if order_line_request.is_sequenced:
                res ={}
            else :
                for obj_order_line in order_line_request.service_order_line_id.service_order_line_request_ids:
                    if obj_order_line.is_sequenced:
                        length = length + 1
                self.write(cr, uid, order_line_request.id, {'is_sequenced': True})
                res[order_line_request.id] = order_line_request.service_order_line_id.sequence + '/' + str(length)
        return res
    
    _name = "service.order.line.request"
    _description = "Service Order Line Request"
    _columns = {
        #----------------Service Report------------------------------
        'is_sequenced': fields.boolean('Sequence'),
        'sequence': fields.function(_get_sequence_request, string='Sequence', readonly=True, type="char", method=True, size=64, store=True),
        'service_order_line_id': fields.many2one('service.order.line', 'Service Order Line'),
        'production_lot_ids': fields.many2many('stock.production.lot', 'production_lot_req',
                             'lot_id', 'order_line_id', 'Product'), 
        'accessories_ids': fields.many2many('product.product', 'accessories_req',
                             'product_id', 'order_line_id', 'Accessories Install'), 
        'name': fields.selection([('1', ' '),
                                  ('installation', 'Installation'),
                                   ('revision', 'Revision'),
                                   ('uninstall', 'Uninstall'),
                                   ('reinstall', 'Reinstall')], 'Service Type'),
        
        'kit_id': fields.many2one('product.product', 'Kit Product'),      
        'serial_number': fields.char('Serial Number', size=64),  
        'economic_num': fields.char('Economic number', size=64),
        'plates': fields.char('Plates', size=64),
        'brand_id': fields.many2one('vehicle.brand','Brand'),
        'vehicle_type_id': fields.many2one('vehicle.type', 'Type of vehicle'),
        'engine_brand_id': fields.many2one('engine.brand', 'Brand'),
        'engine_model_id': fields.many2one('engine.model', 'Model'),
        'installator_id': fields.many2one('hr.employee', 'Installator  Person'),
        'installator_status': fields.boolean('Installator  Status'),
        'transport_method': fields.char('Transport method', size=64),
        'cust_entry_req': fields.char('Entry requirements with the customer', size=64),
        'service_address_id': fields.many2one('res.partner.address', 'Service Address'),
        'contact_person_id': fields.many2one('res.partner.address', 'Contact Person'),
        'phone': fields.char('Phone', size=64),
        'mobile': fields.char('Mobile Phone', size=64),
        'problem_id': fields.many2one('service.problem', 'Problem'),
        'no_ticket': fields.char('No Ticket', size=64),
        'note': fields.text('Note'),
        'service_order_id': fields.many2one('service.order', 'Service Order'),
        'customer_id': fields.related('service_order_id', 'customer_id', type='many2one', relation='res.partner', string='Customer', readonly=True),
        'state': fields.selection([('pending', 'Pending'),
                                   ('done', 'Done')], 'State')
        }
    
    _defaults = {
        'is_sequenced': False,
          }
    
    def create_report(self, cr, uid, ids, context=None):
        if ids:
            objs_request = self.browse(cr, uid, ids)
            for obj in objs_request:
                list_access_ids = []
                list_production_ids = []
                if obj.accessories_ids:
                    for obj_accss in obj.accessories_ids:
                        list_access_ids.append(obj_accss.id)
                if obj.production_lot_ids:
                    for obj_prod in obj.production_lot_ids:
                        list_production_ids.append(obj_prod.id)
                request_id = self.pool.get('service.order.line.report').create(cr, uid, {
                                         'sr_service_type': obj.name,
                                         'sr_production_lot_ids': [(6, 0, list_production_ids)],
                                         'sr_accessories_ids': [(6, 0, list_access_ids)],
                                         'sr_installator_id': obj.installator_id.id,
                                         'sr_transport_method': obj.transport_method,
                                         'sr_cust_entry_req': obj.cust_entry_req,
                                         'sr_service_address_id': obj.service_address_id.id,
                                         'sr_contact_person_id': obj.contact_person_id.id,
                                         'sr_problem_id': obj.problem_id.id,
                                         'sr_economic_num': obj.service_order_line_id.economic_num,
                                         'sr_type': obj.service_order_line_id.plates,
                                         'sr_brand_id': obj.service_order_line_id.brand_id.id,
                                         'sr_vehicle_type_id': obj.service_order_line_id.vehicle_type_id.id,
                                         'sr_engine_brand_id': obj.service_order_line_id.engine_brand_id.id,
                                         'sr_engine_model_id': obj.service_order_line_id.engine_model_id.id,
                                         'service_order_line_id': obj.service_order_line_id.id}, context=context)
                
        return True    
    def onchange_contact_person(self, cr, uid, ids, contact_person_id):
        v = {}
        if contact_person_id:
            contact_person = self.pool.get('res.partner.address').browse(cr, uid, contact_person_id)
            v['phone'] = contact_person.phone
            v['mobile'] = contact_person.mobile
        return {'value': v}
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('service_order_line_id', False):
            service_order_line_id = vals.get('service_order_line_id')
            obj_order_line = self.pool.get('service.order.line').browse(cr, uid, service_order_line_id)
            if 'serial_number' not in vals:
                vals[ 'serial_number' ] = obj_order_line.serial_number
            if 'kit_id' not in vals and obj_order_line.kit_id:
                vals[ 'kit_id' ] = obj_order_line.kit_id.id
            if 'name' not in vals:
                vals[ 'name' ] = obj_order_line.name
        res = super(service_order_line_request, self).create(cr, uid, vals, context)
        return res
     
service_order_line_request()
