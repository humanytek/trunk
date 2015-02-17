# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2011 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
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
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
import netsvc
import decimal_precision as dp

class medicament (osv.osv):
    _inherit = "medical.medicament"


    def get_product_available(self, cr, uid, ids, context=None):
        """ Finds whether product is available or not in particular warehouse.
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        states = context.get('states',[])
        what = context.get('what',())
        if not ids:
            #ids = self.search(cr, uid, [])
            ids = self.pool.get('product.product').search(cr, uid, [])
        res = {}.fromkeys(ids, 0.0)
        if not ids:
            return res

    # TODO: write in more ORM way, less queries, more pg84 magic
        if context.get('shop', False):
            cr.execute('select warehouse_id from sale_shop where id=%s', (int(context['shop']),))
            res2 = cr.fetchone()
            if res2:
                context['warehouse'] = res2[0]

        if context.get('warehouse', False):
            cr.execute('select lot_stock_id from stock_warehouse where id=%s', (int(context['warehouse']),))
            res2 = cr.fetchone()
            if res2:
                context['location'] = res2[0]

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = self.pool.get('stock.location').search(cr, uid, [('name','ilike',context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = []
            wids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
            for w in self.pool.get('stock.warehouse').browse(cr, uid, wids, context=context):
                location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if context.get('compute_child',True):
            child_location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids
        else:
            location_ids = location_ids

        uoms_o = {}
        product2uom = {}
        #for product in self.browse(cr, uid, ids, context=context):
        for product in self.pool.get('product.product').browse(cr, uid, ids, context=context):
            product2uom[product.id] = product.uom_id.id
            uoms_o[product.uom_id.id] = product.uom_id

        results = []
        results2 = []

        from_date = context.get('from_date',False)
        to_date = context.get('to_date',False)
        date_str = False
        date_values = False
        where = [tuple(location_ids),tuple(location_ids),tuple(ids),tuple(states)]
        if from_date and to_date:
            date_str = "date>=%s and date<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "date>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "date<=%s"
            date_values = [to_date]

        prodlot_id = context.get('prodlot_id', False)

    # TODO: perhaps merge in one query.
        if date_values:
            where.append(tuple(date_values))
        if 'in' in what:
            # all moves from a location out of the set to a location in the set
            cr.execute(
                'select sum(product_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id NOT IN %s '\
                'and location_dest_id IN %s '\
                'and product_id IN %s '\
                '' + (prodlot_id and ('and prodlot_id = ' + str(prodlot_id)) or '') + ' '\
                'and state IN %s ' + (date_str and 'and '+date_str+' ' or '') +' '\
                'group by product_id,product_uom',tuple(where))
            results = cr.fetchall()
        if 'out' in what:
            # all moves from a location in the set to a location out of the set
            cr.execute(
                'select sum(product_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id IN %s '\
                'and location_dest_id NOT IN %s '\
                'and product_id  IN %s '\
                '' + (prodlot_id and ('and prodlot_id = ' + str(prodlot_id)) or '') + ' '\
                'and state in %s ' + (date_str and 'and '+date_str+' ' or '') + ' '\
                'group by product_id,product_uom',tuple(where))
            results2 = cr.fetchall()
        uom_obj = self.pool.get('product.uom')
        uoms = map(lambda x: x[2], results) + map(lambda x: x[2], results2)
        if context.get('uom', False):
            uoms += [context['uom']]

        uoms = filter(lambda x: x not in uoms_o.keys(), uoms)
        if uoms:
            uoms = uom_obj.browse(cr, uid, list(set(uoms)), context=context)
            for o in uoms:
                uoms_o[o.id] = o
        #TOCHECK: before change uom of product, stock move line are in old uom.
        context.update({'raise-exception': False})
        for amount, prod_id, prod_uom in results:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                     uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] += amount
        for amount, prod_id, prod_uom in results2:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                    uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] -= amount
        return res

    def _product_qty_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        for id in ids:
            prod_id = self.read(cr,uid,id,['name'])['name'][0]
            #prod_id = self.browse(cr,uid,id,context=context).name.id
            context.update({ 'states': ('done',), 'what': ('in', 'out') })
            stock = self.get_product_available(cr, uid, [prod_id], context=context)
            res[id] = stock.get(prod_id,0.0)
        return res

    def _product_virtual_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        for id in ids:
            prod_id = self.read(cr,uid,id,['name'])['name'][0]
            #prod_id = self.browse(cr,uid,id,context=context).name.id
            context.update({ 'states': ('confirmed','waiting','assigned','done'), 'what': ('in', 'out') })
            stock = self.get_product_available(cr, uid, [prod_id], context=context)
            res[id] = stock.get(prod_id, 0.0)
        return res



    _columns = {
                'qty_available': fields.function(_product_qty_available, type='float',method=True, string='Real Stock', help="Current quantities of products in selected locations or all internal if none have been selected.", digits_compute=dp.get_precision('Product UoM')),
                'virtual_available': fields.function(_product_virtual_available, method=True, type='float', string='Virtual Stock', help="Future stock for this product according to the selected locations or all internal if none have been selected. Computed as: Real Stock - Outgoing + Incoming.", digits_compute=dp.get_precision('Product UoM')),

                'production_state':fields.related('name','state',relation='product.product', type='selection',
                selection=[('',''),('draft', 'In Development'),('sellable','Normal'),('end','End of Lifecycle'),('obsolete','Obsolete')],
                string='Status', readonly=True),
                }

medicament ()