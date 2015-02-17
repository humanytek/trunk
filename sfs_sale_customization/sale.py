# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
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

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def _get_prefix(self, cr, uid, ids, name, args, context=None):
        res = {}
        sequence_prefix = ""
        sequence_pool = self.pool.get('ir.sequence')
        sale_sequence_code_ids = sequence_pool.search(cr, uid, [('code', '=', 'sale.order')], context=context)
        if sale_sequence_code_ids:
            sequence_obj = sequence_pool.browse(cr, uid, sale_sequence_code_ids[0], context=context)
            sequence_prefix = sequence_obj.prefix
        for sale_obj in self.browse(cr, uid, ids, context=context):
            name =sale_obj.name
            sufix = name.replace(sequence_prefix, "")
            if sufix.isdigit():
                sufix = int(sufix)
            else:
                sufix = sale_obj.id
            res[sale_obj.id] = sufix
        return res
    
    _columns = {
                'name_prefix': fields.function(_get_prefix, method=True, string='Reference', type='float',
                                               store={
                                                      'sale.order' : (lambda self, cr, uid, ids, c={}: ids, ['name'], 5),
                                                      },readonly=True),
                }
    _order = 'name_prefix desc'
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: