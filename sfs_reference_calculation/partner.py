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

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _calculate_reference(self, cr, uid, ids, name, args, context=None):
        res = {}
        dict = {}
        for x in range(ord('a'), ord('z') + 1):
             dict[chr(x)] = (x - ord('a') + 1) % 9 or 9
        if context == None:
            context = {}
        for partner_obj in self.browse(cr,uid,ids,context=context):
            ref_calc = ''
            if partner_obj.vat :
                ref_obj='HESA' + partner_obj.vat
                list_ref = list(ref_obj[::-1])

                for ref in list_ref :
                    if ref.lower() in dict :
                        list_ref[list_ref.index(ref)] = dict[ref.lower()]

                sum = 0
                mul_var = 1
                for ref_value in list_ref:
                    ref_ind_value = list(str(int(ref_value) *(mul_var % 2 + 1)))
                    mul_var = mul_var % 2 + 1
                    for val in ref_ind_value:
                        sum += int(val)

                alg_number = str(10 - (sum % 10 or 10))

                vat = partner_obj.vat or ''
                ref_calc = 'HESA' + vat + alg_number
            res[partner_obj.id] = ref_calc.upper()

        return res

    _columns = {
        'reference': fields.function(_calculate_reference, method=True, type='char',
                                     size=128, string='Generated Reference',
                                     store={
                                            'res.partner' : (lambda self, cr, uid, ids,
                                                             c={}: ids, ['vat'], 5),
                                            },readonly=True),
                }

    def _check_ref_length(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.ref and ( len(obj.ref) <= 1 or len(obj.ref) > 30):
            return False
        return True

    _constraints = [
        (_check_ref_length, 'Reference must be between 2 and 30 ', ['ref']),
    ]

res_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
