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

import time
from datetime import datetime
from report import report_sxw

class device(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(device, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_total_amount': self._get_total_amount,
            '_get_repeat': self._get_repeat
        })
            
    def _calculate_device(self, obj_report, service_type, objects):
        emp_obj = objects[0].sr_installator_id
        qty = 0
        qty_service = 0
        amount = 0
        total_amount = 0
        device =""
        for obj in objects:
            if obj_report.service_order_line_id.kit_id == obj.service_order_line_id.kit_id\
                and obj.sr_service_type == service_type:
                    qty = qty + 1
                    qty_service = qty_service + 1
                    if obj.service_order_line_id.kit_id.pack_line_ids:
                        device = obj.service_order_line_id.kit_id.name
                        for obj_pack in obj.service_order_line_id.kit_id.pack_line_ids:
                            qty_service = qty_service + obj_pack.quantity
                    if obj_report.id == obj.id:
                       if obj.service_order_line_id.kit_id:
                            if emp_obj.device_ids:
                                for device_obj in emp_obj.device_ids:
                                    if obj.service_order_line_id.kit_id == device_obj.name:
                                        amount =  amount + device_obj.amount
                            if obj.service_order_line_id.kit_id.pack_line_ids:
                              if emp_obj.device_ids:
                                for obj_pack in obj.service_order_line_id.kit_id.pack_line_ids:
                                        for device_obj in emp_obj.device_ids:
                                            if obj_pack.product_id == device_obj.name:
                                                amount =  amount + (obj_pack.quantity * device_obj.amount)
        total_amount = qty * amount
        return {'qty' : qty, 
                'qty_service' : qty_service,
                'amount' : amount,
                'service_type': service_type,
                'device': device,
                'total_amount' : total_amount}
    
    def _get_repeat(self,objects):
        return_list =[]
        list_service_type = ['installation','revision',
                             'uninstall','reinstall']
        for service_type in list_service_type:
            chk_product =[]
            for obj in objects:
                if obj.sr_service_type == service_type:
                    if obj.service_order_line_id.kit_id.id not in chk_product:
                        return_list.append( self._calculate_device(obj, service_type, objects))
                        chk_product.append(obj.service_order_line_id.kit_id.id)
        return return_list
        
    def _get_total_amount(self,objects):
        qty = 0
        amount = 0
        emp_obj = objects[0].sr_installator_id
        for obj in objects: 
                if obj.service_order_line_id.kit_id:
                    if emp_obj.device_ids:
                            for device_obj in emp_obj.device_ids:
                                if obj.service_order_line_id.kit_id == device_obj.name:
                                    amount =  amount + device_obj.amount
                    if obj.service_order_line_id.kit_id.pack_line_ids:
                        if emp_obj.device_ids:
                            for obj_pack in obj.service_order_line_id.kit_id.pack_line_ids:
                                    for device_obj in emp_obj.device_ids:
                                        if obj_pack.product_id == device_obj.name:
                                            amount =  amount + (obj_pack.quantity * device_obj.amount)
        return amount

report_sxw.report_sxw('report.device.commission', 'service.order.line.report',
                       'addons/sfs_service_order/report/device_commission.rml',
                        parser=device, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: