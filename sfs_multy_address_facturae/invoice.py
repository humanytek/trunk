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

from osv import osv, fields
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
                'address_id':fields.many2one('res.partner.address','Domicilio de expedicion'),
                'partners_id': fields.related('company_id', 'partner_id', type='many2one', relation='res.partner', string='Company'),
                }
    
    def onchange_company_id(self, cr, uid, ids, company_id, part_id, type, invoice_line, currency_id):
        res = super(account_invoice,self).onchange_company_id(cr, uid, ids, company_id, part_id, type, invoice_line, currency_id)
        val = {}
        if not company_id:
            return res
        company_obj = self.pool.get('res.company').browse(cr, uid, company_id, context={})
        if company_obj:
            company_add = company_obj.partner_id.id
        val = {
               'partners_id': company_add
              }
        res['value'].update(val)
        return res
    
    def _get_facturae_invoice_dict_data(self, cr, uid, ids, context=None):
        res = super(account_invoice, self)._get_facturae_invoice_dict_data(cr, uid, ids, context=context)
        for invoice_obj in self.browse(cr, uid, ids, context=context):
            elec_invoice_obj = invoice_obj.address_id
            if not elec_invoice_obj:
                raise osv.except_osv(_('Error !'),
                        _('Domicilio de expedicion not defined'))
            if res:
                address_data = res[0]['Comprobante']['Emisor']['ExpedidoEn']
                address_data= {
                               'calle': elec_invoice_obj.street and elec_invoice_obj.street.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                               'noExterior': elec_invoice_obj.street3 and elec_invoice_obj.street3.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                               'noInterior': elec_invoice_obj.street4 and elec_invoice_obj.street4.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                               'colonia':  elec_invoice_obj.street2 and elec_invoice_obj.street2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A' ,
                               'localidad': elec_invoice_obj.city2 and elec_invoice_obj.city2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                               'municipio': elec_invoice_obj.city and elec_invoice_obj.city.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                               'estado': elec_invoice_obj.state_id and elec_invoice_obj.state_id.name and elec_invoice_obj.state_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '' ,
                               'pais': elec_invoice_obj.country_id and elec_invoice_obj.country_id.name and elec_invoice_obj.country_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')or '',
                               'codigoPostal': elec_invoice_obj.zip and elec_invoice_obj.zip.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                               }
                res[0]['Comprobante']['Emisor']['ExpedidoEn'] = address_data
        return res

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: