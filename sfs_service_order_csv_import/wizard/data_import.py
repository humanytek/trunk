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

from datetime import datetime
import time

from osv import fields, osv
import string
import time
import base64
from tools.translate import _
import csv
import StringIO
import netsvc

def process_csv_data(csv_data):
    csv_data_lines = base64.decodestring(csv_data).replace("\r", "").split("\n")
    datafile = StringIO.StringIO(base64.decodestring(csv_data))
    csvReader = csv.reader(datafile, dialect='excel')
    ret = []
    for line in csvReader:
        cline = []
        for elm in line:
            cline.append(elm.replace('+ACI-', '').replace('+AC0-',''))
        ret.append(cline)
    return ret

def _get_models(self, cr, uid, context=None):
    models = [
        ('service.order', 'Service Order'),
        ('service.order.line', 'Service Order Line')
        ]
    return models

class data_import(osv.osv_memory):

    def _create_service_order(self, cr, uid, obj, data_list, index, context=None):
        lines = 0
        vals = {}
        count = 0
        summary = summary1 = ''
        partner_obj = self.pool.get('res.partner')
        picking_obj = self.pool.get('stock.picking')
        sale_order_obj = self.pool.get('sale.order')
        for data in data_list[1:]:
            if 'Source (delivery order)' in index and 'Sale Order' in index and 'Sequence' in index:
                count += 1
                if data[index['Customer']]:
                    lines += 1
                    customer_ids = partner_obj.search(cr, uid, [('name', '=', data[index['Customer']])], context=context)
                    if customer_ids:
                        res = obj.onchange_customer(cr, uid, [], customer_ids[0])['value']
                        vals['customer_id'] = customer_ids[0],
                        vals.update(res)
                    else:
                        summary1 += 'Customer %s in Line %s is not Found\n'%(data[index['Customer']],count)
                else:
                    summary1 += 'Customer missing in Line %s\n'%count
                    continue
                
                if data[index['Source (delivery order)']]:
                    lines += 1
                    picking_ids = picking_obj.search(cr, uid, [('name', '=', data[index['Source (delivery order)']])], context=context)
                    if picking_ids:
                        vals['source_id'] = picking_ids[0]
                    else:
                        summary1 += 'Source (delivery order) %s in Line %s is not Found\n'%(data[index['Source (delivery order)']],count)
                else:
                    summary1 += 'Source (delivery order) missing in Line %s\n'%count
                    continue
                
                if data[index['Sale Order']]:
                    lines += 1
                    sale_order_ids = sale_order_obj.search(cr, uid, [('name', '=', data[index['Sale Order']])], context=context)
                    
                    if sale_order_ids:
                        vals['sale_order_id'] = sale_order_ids[0]
                    else:
                        summary1 += 'Sale Order %s in Line %s is not Found\n'%(data[index['Sale Order']],count)
                else:
                    summary1 += 'Sale Order missing in Line %s\n'%count
                    continue
                
                if 'Sequence' in index and data[index['Sequence']]:
                    vals['name'] = data[index['Sequence']]
                if 'Proposed Date' in index and data[index['Proposed Date']]:
                    vals['proposed_date_'] = data[index['Proposed Date']]
                if 'Proposed Time' in index and data[index['Proposed Time']]:
                    vals['proposed_time_'] = data[index['Proposed Time']]
                if 'Validity/Life' in index and data[index['Validity/Life']]:
                    vals['validity'] = data[index['Validity/Life']]
                if 'State Of Product' in index and data[index['State Of Product']]:
                    if data[index['State Of Product']] == 'Test':
                        vals['product_state'] = 'test'
                    elif data[index['State Of Product']] == 'Sale':
                        vals['product_state'] = 'sale'
                    elif data[index['State Of Product']] == 'Rent':
                        vals['product_state'] = 'rent'
                    else:
                        vals['product_state'] = data[index['State Of Product']]
                obj.create(cr, uid, vals, context=context)
            else:
                raise osv.except_osv(_('Source (delivery order) Not Found!'), _('Source (delivery order) Column Not Found'))
                
        return summary + summary1
    
    def _create_service_order_line(self, cr, uid, obj, data_list, index, context=None):
        lines = 0
        vals = {}
        count = 0
        summary = summary1 = ''
        product_obj = self.pool.get('product.product')
        service_order_obj = self.pool.get('service.order')
        vehicle_brand_obj = self.pool.get('vehicle.brand')
        vehicle_type_obj = self.pool.get('vehicle.type')
        engine_brand_obj = self.pool.get('engine.brand')
        engine_model_obj = self.pool.get('engine.model')
        hr_employee_obj = self.pool.get('hr.employee')
        service_problem_obj = self.pool.get('service.problem')
        service_order_line_request_obj = self.pool.get('service.order.line.request')
        service_order_line_report_obj = self.pool.get('service.order.line.report')
        res_partner_address_obj = self.pool.get('res.partner.address')
        vehicle_model_obj = self.pool.get('vehicle.model')
        vehicle_protocol_obj = self.pool.get('vehicle.protocol')
        service_order_line_id = False
        service_order_id = False
        kit_product_id = False
        for data in data_list[1:]:
            if 'Service Order' in index and 'Kit Product' in index:
             if data[index['Service Order']]: 
                count += 1
                if data[index['Service Order']]:
                    lines += 1
                    service_order_ids = service_order_obj.search(cr, uid, [('name', '=', data[index['Service Order']])], context=context)
                    if service_order_ids:
                        vals['service_order_id'] = service_order_ids[0]
                        service_order_id = service_order_ids[0]
                    else:
                        summary1 += 'Service Order %s in Line %s is not Found\n'%(data[index['Service Order']],count)
                else:
                    summary1 += 'Service Order missing in Line %s\n'%count
                    continue
                
                if data[index['Vehicle Brand']]:
                    lines += 1
                    vehicle_brand_ids = vehicle_brand_obj.search(cr, uid, [('name', '=', data[index['Vehicle Brand']])], context=context)
                    if vehicle_brand_ids:
                        vals['brand_id'] = vehicle_brand_ids[0]
                    else:
                        summary1 += 'Vehicle Brand %s in Line %s is not Found\n'%(data[index['Vehicle Brand']],count)
                else:
                    summary1 += 'Vehicle Brand missing in Line %s\n'%count
                    continue
                
                if data[index['Kit Product']]:
                    lines += 1
                    product_ids = product_obj.search(cr, uid, [('name', '=', data[index['Kit Product']])], context=context)
                    if product_ids:
                        vals['kit_id'] = product_ids[0]
                        kit_product_id = product_ids[0]
                        kit_product_obj = product_obj.browse(cr, uid, product_ids[0])
                        if kit_product_obj.pack_fixed_price:
                          
                            product_pack_ids = []
                            for products_pack in kit_product_obj.pack_line_ids:
                                product_pack_ids.append(products_pack.product_id.id)
                            
                            vals['accessories_ids'] = [(6,0,product_pack_ids)]    
                    else:
                        summary1 += 'Kit Product %s in Line %s is not Found\n'%(data[index['Kit Product']],count)
                else:
                    summary1 += 'Kit Product missing in Line %s\n'%count
                    continue
                
                if data[index['Type of vehicle']]:
                    lines += 1
                    vehicle_type_ids = vehicle_type_obj.search(cr, uid, [('name', '=', data[index['Type of vehicle']])], context=context)
                    if vehicle_type_ids:
                        vals['vehicle_type_id'] = vehicle_type_ids[0]
                    else:
                        summary1 += 'Type of vehicle %s in Line %s is not Found\n'%(data[index['Type of vehicle']],count)
                else:
                    summary1 += 'Type of vehicle missing in Line %s\n'%count
                    continue
                
                if data[index['Engine Brand']]:
                    lines += 1
                    engine_brand_ids = engine_brand_obj.search(cr, uid, [('name', '=', data[index['Engine Brand']])], context=context)
                    if engine_brand_ids:
                        vals['engine_brand_id'] = engine_brand_ids[0]
                    else:
                        summary1 += 'Engine Brand %s in Line %s is not Found\n'%(data[index['Engine Brand']],count)
                else:
                    summary1 += 'Engine Brand missing in Line %s\n'%count
                    continue
                
                if data[index['Engine Model']]:
                    lines += 1
                    eengine_model_ids = engine_model_obj.search(cr, uid, [('name', '=', data[index['Engine Model']])], context=context)
                    if eengine_model_ids:
                        vals['engine_model_id'] = eengine_model_ids[0]
                    else:
                        summary1 += 'Engine Model %s in Line %s is not Found\n'%(data[index['Engine Model']],count)
                else:
                    summary1 += 'Engine Model missing in Line %s\n'%count
                    continue
                
                if 'Sequence' in index and data[index['Sequence']]:
                    vals['sequence'] = data[index['Sequence']]
                if 'Serial Number' in index and data[index['Serial Number']]:
                    vals['serial_number'] = data[index['Serial Number']]
                if 'Economic number' in index and data[index['Economic number']]:
                    vals['economic_num'] = data[index['Economic number']]
                if 'Plates' in index and data[index['Plates']]:
                    vals['plates'] = data[index['Plates']]
                if 'Note' in index and data[index['Note']]:
                    vals['note'] = data[index['Note']]
                if 'Service Type' in index and data[index['Service Type']]:
                    if data[index['Service Type']] == 'Installation':
                        vals['name'] = 'installation'
                    elif data[index['Service Type']] == 'Revision':
                        vals['name'] = 'revision'
                    elif data[index['Service Type']] == 'Uninstall':
                        vals['name'] = 'uninstall'
                    elif data[index['Service Type']] == 'Reinstall':
                        vals['name'] = 'reinstall'
                    else:
                        vals['name'] = data[index['Service Type']]
                    
                service_order_line_id = obj.create(cr, uid, vals, context=context)
                vals = {}
#                if service_order_line_id:
#                    vals['service_order_line_id'] = service_order_line_id
#                    if 'Order Line Service Request/Sequence' in index and data[index['Order Line Service Request/Sequence']]:
#                        vals['sequence'] = data[index['Order Line Service Request/Sequence']]
#                    
#                    service_order_line_request_obj.create(cr, uid, vals, context=context)
             if data[index['Order Line Service Request/Sequence']]:
                vals={}
                
                if service_order_line_id:
                    if service_order_id:
                            vals['service_order_id'] = service_order_id
                    if data[index['Order Line Service Request/Vehicle Brand']]:
                        lines += 1
                        vehicle_brand_ids = vehicle_brand_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Request/Vehicle Brand']])], context=context)
                        if vehicle_brand_ids:
                            vals['brand_id'] = vehicle_brand_ids[0]
                        else:
                            summary1 += 'Order Line Service Request/Vehicle Brand %s in Line %s is not Found\n'%(data[index['Order Line Service Request/Vehicle Brand']],count)
                    else:
                        summary1 += 'Order Line Service Request/Vehicle Brand missing in Line %s\n'%count
                        continue
                    if data[index['Order Line Service Request/Kit Product']]:
                        lines += 1
                        product_ids = product_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Request/Kit Product']])], context=context)
                        if product_ids:
                            vals['kit_id'] = product_ids[0]
                            kit_product_id = product_ids[0]
                            kit_product_obj = product_obj.browse(cr, uid, product_ids[0])
                            if kit_product_obj.pack_fixed_price:
                          
                                product_pack_ids = []
                                for products_pack in kit_product_obj.pack_line_ids:
                                    product_pack_ids.append(products_pack.product_id.id)
                                    vals['accessories_ids'] = [(6,0,product_pack_ids)]    
                            else:
                                summary1 += 'Order Line Service Request/Kit Product %s in Line %s is not Found\n'%(data[index['Order Line Service Request/Kit Product']],count)
                        else:
                            summary1 += 'Order Line Service Request/Kit Product missing in Line %s\n'%count
                            continue
                    if data[index['Order Line Service Request/Type of vehicle']]:
                        lines += 1
                        vehicle_type_ids = vehicle_type_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Request/Type of vehicle']])], context=context)
                        if vehicle_type_ids:
                            vals['vehicle_type_id'] = vehicle_type_ids[0]
                        else:
                            summary1 += 'Order Line Service Request/Type of vehicle %s in Line %s is not Found\n'%(data[index['Order Line Service Request/Type of vehicle']],count)
                    else:
                        summary1 += 'Order Line Service Request/Type of vehicle missing in Line %s\n'%count
                        continue
                    if data[index['Order Line Service Request/Engine Brand']]:
                        lines += 1
                        engine_brand_ids = engine_brand_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Request/Engine Brand']])], context=context)
                        if engine_brand_ids:
                            vals['engine_brand_id'] = engine_brand_ids[0]
                        else:
                            summary1 += 'Order Line Service Request/Engine Brand %s in Line %s is not Found\n'%(data[index['Order Line Service Request/Engine Brand']],count)
                    else:
                        summary1 += 'Order Line Service Request/Engine Brand missing in Line %s\n'%count
                        continue
                    if data[index['Order Line Service Request/Engine Model']]:
                        lines += 1
                        engine_model_ids = engine_model_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Request/Engine Model']])], context=context)
                        if engine_model_ids:
                            vals['engine_model_id'] = engine_model_ids[0]
                        else:
                            summary1 += 'Order Line Service Request/Engine Model %s in Line %s is not Found\n'%(data[index['Order Line Service Request/Engine Model']],count)
                    else:
                        summary1 += 'Order Line Service Request/Engine Model missing in Line %s\n'%count
                        continue
                    if data[index['Order Line Service Request/Installator  Person']]:
                        lines += 1
                        hr_employee_ids = hr_employee_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Request/Installator  Person']])], context=context)
                        if hr_employee_ids:
                            vals['installator_id'] = hr_employee_ids[0]
                        else:
                            summary1 += 'Order Line Service Request/Installator  Person %s in Line %s is not Found\n'%(data[index['Order Line Service Request/Installator  Person']],count)
                    else:
                        summary1 += 'Order Line Service Request/Installator  Person missing in Line %s\n'%count
                        continue
                    
                    if data[index['Order Line Service Request/Service Address']]:
                        lines += 1
                        res_partner_address_ids = res_partner_address_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Request/Service Address']])], context=context)
                        if res_partner_address_ids:
                            vals['service_address_id'] = res_partner_address_ids[0]
                        else:
                            summary1 += 'Order Line Service Request/Service Address %s in Line %s is not Found\n'%(data[index['Order Line Service Request/Service Address']],count)
                    else:
                        summary1 += 'Order Line Service Request/Service Address missing in Line %s\n'%count
                        continue
                    
                    if data[index['Order Line Service Request/Contact Person']]:
                        lines += 1
                        res_partner_address_ids = res_partner_address_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Request/Contact Person']])], context=context)
                        if res_partner_address_ids:
                            vals['contact_person_id'] = res_partner_address_ids[0]
                        else:
                            summary1 += 'Order Line Service Request/Contact Person %s in Line %s is not Found\n'%(data[index['Order Line Service Request/Contact Person']],count)
                    else:
                        summary1 += 'Order Line Service Request/Contact Person missing in Line %s\n'%count
                        continue
                    
                    if data[index['Order Line Service Request/Problem']]:
                        lines += 1
                        service_problem_ids = service_problem_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Request/Problem']])], context=context)
                        if service_problem_ids:
                            vals['problem_id'] = service_problem_ids[0]
                        else:
                            summary1 += 'Order Line Service Request/Problem %s in Line %s is not Found\n'%(data[index['Order Line Service Request/Problem']],count)
                    else:
                        summary1 += 'Order Line Service Request/Problem missing in Line %s\n'%count
                        continue
                    if 'Order Line Service Request/Transport method' in index and data[index['Order Line Service Request/Transport method']]:
                        vals['transport_method'] = data[index['Order Line Service Request/Transport method']]
                    if 'Order Line Service Request/Entry requirements with the customer' in index and data[index['Order Line Service Request/Entry requirements with the customer']]:
                        vals['cust_entry_req'] = data[index['Order Line Service Request/Entry requirements with the customer']]
                    if 'Order Line Service Request/Phone' in index and data[index['Order Line Service Request/Phone']]:
                        vals['phone'] = data[index['Order Line Service Request/Phone']]  
                    if 'Order Line Service Request/Mobile Phone' in index and data[index['Order Line Service Request/Mobile Phone']]:
                        vals['mobile'] = data[index['Order Line Service Request/Mobile Phone']]   
                    if 'Order Line Service Request/No Ticket' in index and data[index['Order Line Service Request/No Ticket']]:
                        vals['no_ticket'] = data[index['Order Line Service Request/No Ticket']]                  
                    if 'Order Line Service Request/Sequence' in index and data[index['Order Line Service Request/Sequence']]:
                        vals['sequence'] = data[index['Order Line Service Request/Sequence']]
                    if 'Order Line Service Request/Serial Number' in index and data[index['Order Line Service Request/Serial Number']]:
                        vals['serial_number'] = data[index['Order Line Service Request/Serial Number']]
                    if 'Order Line Service Request/Economic number' in index and data[index['Order Line Service Request/Economic number']]:
                        vals['economic_num'] = data[index['Order Line Service Request/Economic number']]
                    if 'Order Line Service Request/Plates' in index and data[index['Order Line Service Request/Plates']]:
                        vals['plates'] = data[index['Order Line Service Request/Plates']]
                    if 'Order Line Service Request/Note' in index and data[index['Order Line Service Request/Note']]:
                        vals['note'] = data[index['Order Line Service Request/Note']]
                    if 'Order Line Service Request/Service Type' in index and data[index['Order Line Service Request/Service Type']]:
                        if data[index['Order Line Service Request/Service Type']] == 'Installation':
                            vals['name'] = 'installation'
                        elif data[index['Order Line Service Request/Service Type']] == 'Revision':
                            vals['name'] = 'revision'
                        elif data[index['Order Line Service Request/Service Type']] == 'Uninstall':
                            vals['name'] = 'uninstall'
                        elif data[index['Order Line Service Request/Service Type']] == 'Reinstall':
                            vals['name'] = 'reinstall'
                        else:
                            vals['name'] = data[index['Order Line Service Request/Service Type']]
                    vals['service_order_line_id'] = service_order_line_id
                    if 'Order Line Service Request/Sequence' in index and data[index['Order Line Service Request/Sequence']]:
                        vals['sequence'] = data[index['Order Line Service Request/Sequence']]
                    service_order_line_request_obj.create(cr, uid, vals, context=context)
                    
                
             if data[index['Order Line Service Report/Sequence']]:
                if service_order_line_id:
                    if data[index['Order Line Service Report/Vehicle Brand']]:
                        lines += 1
                        vehicle_brand_ids = vehicle_brand_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Vehicle Brand']])], context=context)
                        if vehicle_brand_ids:
                            vals['sr_brand_id'] = vehicle_brand_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Vehicle Brand %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Vehicle Brand']],count)
                    else:
                        summary1 += 'Order Line Service Report/Vehicle Brand missing in Line %s\n'%count
                        continue
                    if kit_product_id:
                            kit_product_obj = product_obj.browse(cr, uid, kit_product_id)
                            if kit_product_obj.pack_fixed_price:
                                product_pack_ids = []
                                for products_pack in kit_product_obj.pack_line_ids:
                                    product_pack_ids.append(products_pack.product_id.id)
                                    vals['sr_accessories_ids'] = [(6,0,product_pack_ids)]    
                                                  
                    if data[index['Order Line Service Report/Type of vehicle']]:
                        lines += 1
                        vehicle_type_ids = vehicle_type_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Type of vehicle']])], context=context)
                        if vehicle_type_ids:
                            vals['sr_vehicle_type_id'] = vehicle_type_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Type of vehicle %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Type of vehicle']],count)
                    else:
                        summary1 += 'Order Line Service Report/Type of vehicle missing in Line %s\n'%count
                        continue
                    if data[index['Order Line Service Report/Engine Brand']]:
                        lines += 1
                        engine_brand_ids = engine_brand_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Engine Brand']])], context=context)
                        if engine_brand_ids:
                            vals['sr_engine_brand_id'] = engine_brand_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Engine Brand %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Engine Brand']],count)
                    else:
                        summary1 += 'Order Line Service Report/Engine Brand missing in Line %s\n'%count
                        continue
                    if data[index['Order Line Service Report/Engine Model']]:
                        lines += 1
                        engine_model_ids = engine_model_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Engine Model']])], context=context)
                        if engine_model_ids:
                            vals['sr_engine_model_id'] = engine_model_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Engine Model %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Engine Model']],count)
                    else:
                        summary1 += 'Order Line Service Report/Engine Model missing in Line %s\n'%count
                        continue
                    if data[index['Order Line Service Report/Installator  Person']]:
                        lines += 1
                        hr_employee_ids = hr_employee_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Installator  Person']])], context=context)
                        if hr_employee_ids:
                            vals['sr_installator_id'] = hr_employee_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Installator  Person %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Installator  Person']],count)
                    else:
                        summary1 += 'Order Line Service Report/Installator  Person missing in Line %s\n'%count
                        continue
                    
                    if data[index['Order Line Service Report/Service Address']]:
                        lines += 1
                        res_partner_address_ids = res_partner_address_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Service Address']])], context=context)
                        if res_partner_address_ids:
                            vals['sr_service_address_id'] = res_partner_address_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Service Address %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Service Address']],count)
                    else:
                        summary1 += 'Order Line Service Report/Service Address missing in Line %s\n'%count
                        continue
                    
                    if data[index['Order Line Service Report/Contact Person']]:
                        lines += 1
                        res_partner_address_ids = res_partner_address_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Contact Person']])], context=context)
                        if res_partner_address_ids:
                            vals['sr_contact_person_id'] = res_partner_address_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Contact Person %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Contact Person']],count)
                    else:
                        summary1 += 'Order Line Service Report/Contact Person missing in Line %s\n'%count
                        continue
                    
                    if data[index['Order Line Service Report/Problem']]:
                        lines += 1
                        service_problem_ids = service_problem_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Problem']])], context=context)
                        if service_problem_ids:
                            vals['sr_problem_id'] = service_problem_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Problem %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Problem']],count)
                    else:
                        summary1 += 'Order Line Service Report/Problem missing in Line %s\n'%count
                        continue
                    
                    if data[index['Order Line Service Report/Vehicle Model']]:
                        lines += 1
                        vehicle_model_ids = vehicle_model_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Vehicle Model']])], context=context)
                        if vehicle_model_ids:
                            vals['sr_model_id'] = vehicle_model_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Vehicle Model %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Vehicle Model']],count)
                    else:
                        summary1 += 'Order Line Service Report/Vehicle Model missing in Line %s\n'%count
                        continue
                    
                    if data[index['Order Line Service Report/Protocol']]:
                        lines += 1
                        vehicle_protocol_ids = vehicle_protocol_obj.search(cr, uid, [('name', '=', data[index['Order Line Service Report/Protocol']])], context=context)
                        if vehicle_protocol_ids:
                            vals['sr_protocol_id'] = vehicle_protocol_ids[0]
                        else:
                            summary1 += 'Order Line Service Report/Protocol %s in Line %s is not Found\n'%(data[index['Order Line Service Report/Protocol']],count)
                    else:
                        summary1 += 'Order Line Service Report/Protocol missing in Line %s\n'%count
                        continue
                                
                    if 'Order Line Service Report/Sequence' in index and data[index['Order Line Service Report/Sequence']]:
                        vals['sequence'] = data[index['Order Line Service Report/Sequence']]
                    
                    if 'Order Line Service Report/Economic number' in index and data[index['Order Line Service Report/Economic number']]:
                        vals['sr_economic_num'] = data[index['Order Line Service Report/Economic number']]
                    if 'Order Line Service Report/Plates' in index and data[index['Order Line Service Report/Plates']]:
                        vals['sr_type'] = data[index['Order Line Service Report/Plates']]
                    if 'Order Line Service Report/Note' in index and data[index['Order Line Service Report/Note']]:
                        vals['sr_notes'] = data[index['Order Line Service Report/Note']]
                    if 'Order Line Service Report/Service Type' in index and data[index['Order Line Service Report/Service Type']]:
                        if data[index['Order Line Service Report/Service Type']] == 'Installation':
                            vals['sr_service_type'] = 'installation'
                        elif data[index['Order Line Service Report/Service Type']] == 'Revision':
                            vals['sr_service_type'] = 'revision'
                        elif data[index['Order Line Service Report/Service Type']] == 'Uninstall':
                            vals['sr_service_type'] = 'uninstall'
                        elif data[index['Order Line Service Report/Service Type']] == 'Reinstall':
                            vals['sr_service_type'] = 'reinstall'
                        else:
                            vals['sr_service_type'] = data[index['Order Line Service Report/Service Type']]
                    
                    if 'Order Line Service Report/Date start installation' in index and data[index['Order Line Service Report/Date start installation']]:
                        vals['sr_inst_start_date'] = data[index['Order Line Service Report/Date start installation']]
                    if 'Order Line Service Report/Date end installation' in index and data[index['Order Line Service Report/Date end installation']]:
                        vals['sr_inst_end_date'] = data[index['Order Line Service Report/Date end installation']]
                    if 'Order Line Service Report/Year' in index and data[index['Order Line Service Report/Year']]:
                        vals['sr_year'] = data[index['Order Line Service Report/Year']]
                    if 'Order Line Service Report/Solution' in index and data[index['Order Line Service Report/Solution']]:
                        vals['sr_solution'] = data[index['Order Line Service Report/Solution']]
                    if 'Order Line Service Report/Serial number' in index and data[index['Order Line Service Report/Serial number']]:
                        vals['sr_engine_serial_no'] = data[index['Order Line Service Report/Serial number']]
                    vals['service_order_line_id'] = service_order_line_id
                    
                    service_order_line_report_obj.create(cr, uid, vals, context=context)       
                    
                    
                    
                    
                    
                    
            else:
                raise osv.except_osv(_('Service Order Not Found!'), _('Service Order Column Not Found'))
                
        return summary + summary1
    
    def import_csv(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids)[0]
        data_list = process_csv_data(data['csv_file'])
        index = {}
        for x in data_list[0]:
            index[x] = data_list[0].index(x)
        model = data['model']
        obj = self.pool.get(model)
        result = ''
        
        if model == 'service.order':
            result = self._create_service_order(cr, uid, obj, data_list, index, context=context)
        elif model == 'service.order.line':
            result = self._create_service_order_line(cr, uid, obj, data_list, index, context=context)
        
        return {'type': 'ir.actions.act_window_close'}

    _name='data.import'
    _columns = {
        'csv_file': fields.binary('CSV File', filters="*.csv", required=True),
        'summary': fields.text('Summary', readonly=True),
        'model': fields.selection(_get_models, 'Model', required=True),
        'datas_fname': fields.char('Filename', size=256),
        }

data_import()
