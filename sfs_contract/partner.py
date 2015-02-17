# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    conatct@zbeanztech.com
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

class partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
                'legal_rep_name' : fields.char('Legal Representative Name',size=64),
                'public_writing_no':fields.char('Public Writing Number',size=64),
                'public_writing_date':fields.date('Public Writing Date'),
                'notary_person' : fields.char('Notary Person Name',size=64),
                'notary_office_no': fields.char('Notary Office Number',size=64),
                'notary_office_loc':fields.char('Notary Office Location',size=64),
                'rpp_folio' : fields.char('RPP Folio Number',size=64),
                'rep_rpp_folio' : fields.char('Representative RPP Folio Number',size=64),
                'attorney_rep_no':fields.char('Attorney Representative Number',size=64),
                'attorney_date' : fields.date('Power of Attorney Date'),
                'notary_person_no': fields.char('Notary Person Number',size=64),
                'city_notary_person': fields.char('City of Notary Person',size=64),
                'guarantor_name':fields.char('Guarantor Name',size=64),
                'guarantor_street':fields.char('Street',size=64),
                'guarantor_street1':fields.char('Street2',size=64),
                'guarantor_city':fields.char('City',size=64),
                'guarantor_state':fields.char('State',size=64),
                'guarantor_zip':fields.char('Zip',size=64),
                'guarantor_phone':fields.char('Phone',size=64),
                'moratory_interest' :fields.integer('Moratory Interest Rate(%)'),
                }
partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: