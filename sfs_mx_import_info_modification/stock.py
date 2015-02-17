# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2011 ZestyBeanz Technologies Pvt. Ltd.
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
##
##############################################################################

import time
from osv import osv
from osv import fields
from tools.translate import _

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    def action_done(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            self.pool.get('stock.move').write(cr, uid, [x.id for x in inv.move_ids], {'constrain':True,}, context=context)
        return super(stock_inventory, self).action_done(cr, uid, ids, context=None)
stock_inventory()
class stock_move(osv.osv):
    """
    stock_move for validations in the move of inventory
    """
    _inherit = 'stock.move'
    _columns = {
                'constrain' : fields.boolean('constrain')
                }

    def action_scrap(self, cr, uid, ids, quantity, location_id, context=None):
        if context and context.get('constrain', False)  :
            self.write(cr,uid,ids,{'constrain' :True})
        return super(stock_move, self).action_scrap(cr, uid, ids,quantity, location_id, context=None)
    def action_consume(self, cr, uid, ids, quantity, location_id=False, context=None):

        if context and context.get('constrain', False)  :
            self.write(cr,uid,ids,{'constrain' :True})
        return super(stock_move, self).action_consume(cr, uid, ids, quantity, location_id=False, context=None)
    def action_done(self, cr, uid, ids, context=None):
        if context and context.get('constrain', False)  :
            self.write(cr,uid,ids,{'constrain' :True})
        return super(stock_move, self).action_done(cr, uid, ids, context=None)
    def _check_import_info(self, cr, uid, ids, context=None):
        """ Checks track lot with import information is assigned to stock move or not.
        @return: True or False
        """
        for move in self.browse(cr, uid, ids, context=context):
            #Check if i need to verify the track for import info.

            ex = True

            if move.constrain:
                return True
            if not move.tracking_id and \
               (move.state == 'done' and \
               ( \
                   (move.product_id.pack_control and move.location_id.usage == 'production') or \
                   (move.product_id.pack_control and move.location_id.usage == 'internal') or \
                   (move.product_id.pack_control and move.location_id.usage == 'inventory') or \
                   (move.product_id.pack_control and move.location_dest_id.usage == 'production') or \
                   (move.product_id.pack_control and move.location_id.usage == 'supplier') or \
                   (move.product_id.pack_control and move.location_dest_id.usage == 'customer') \
               )): ex = False


            if not self._check_if_product_in_track(cr, uid, ids, move, context):
                ex = False
            if not self._check_product_qty(cr, uid, [move.id], context):
                    ex = False
        return ex

    _constraints = [(_check_import_info,'You must assign a track lot with import information for this product, if it is assigned verify if you have enought products planified on this import document or at least if the product exist in the list of products in this import document, if you are trying to generate a new pack with the wizard it is not possible if the product is checked as Pack Control, check with your product manager to make the analisys of the situation.\nOther error can be on product_qty field,  Product qty is bigger than product qty on import info.',['tracking_id'])]


stock_move()
