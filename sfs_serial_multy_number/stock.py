from osv import osv, fields
from datetime import datetime
from tools.translate import _

#class stock_picking(osv.osv):############TO DO
#    _inherit = "stock.picking"
#
#    def action_process(self, cr, uid, ids, context=None):
#        if context is None: context = {}
#        partial_id = self.pool.get("stock.partial.pick").create(
#            cr, uid, {}, context=dict(context, active_ids=ids))
#        return {
#            'name':_("Products to Process"),
#            'view_mode': 'form',
#            'view_id': False,
#            'view_type': 'form',
#            'res_model': 'stock.partial.pick',
#            'res_id': partial_id,
#            'type': 'ir.actions.act_window',
#            'nodestroy': True,
#            'target': 'new',
#            'domain': '[]',
#            'context': dict(context, active_ids=ids)
#        }
#stock_picking()

class stock_move(osv.osv):
    """inherits fromk stock_move for checks expired prodlots"""
    _inherit = "stock.move"

    def _check_prodlot_expiration(self, cr, uid, ids):
        """checks if prodlot is expired and is trying move it to internal or customer location"""
        for move in self.browse(cr, uid, ids):
            if move.prodlot_id and move.location_dest_id:
                if move.prodlot_id.expired and move.location_dest_id.usage in ['internal', 'customer']:
                    return False
        return True

    _columns = {
                'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot/Part Number', states={'done': [('readonly', True)]}, help="Production lot/Part Number is used to put a serial number on the production", select=True),
                }
    _constraints = [
    (_check_prodlot_expiration, _('Cannot move an expired production lot to internal or customer location'), ['expired']),
    ]

    def eval_onchange_lot_date(self, cr, uid, res, prodlot_id = False):
        """overwrites this event for shows a warning if the production lot selected is expired"""
        prodlot = prodlot_id or ((res.get('value') and res['value'].get('prodlot_id')) and res['value']['prodlot_id'] or False)
        if res.get('warning', False):
            res['value']=res.get('value') and res['value'].update({'prodlot_id': False}) or {'prodlot_id': False}
            return res
        elif prodlot:
            res['value']={'prodlot_id': prodlot}
            obj_prodlot_id = self.pool.get('stock.production.lot').browse(cr, uid, prodlot)
            if obj_prodlot_id.expired:
                res['warning'] = {
                    'title': _('Part Number Expired!'),
                    'message': _('This production lot is expired'),
                        }
                return {'warning': res['warning'], 'value': res['value']}
        return res

    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False, loc_id=False, product_id=False, uom_id=False, context=None):
        """overwrites this event for shows a warning if the production lot selected is on alert"""
        if context is None: context = {}
        if not prodlot_id or not loc_id:
            return {}

        res = super(stock_move, self).onchange_lot_id(cr, uid, ids, prodlot_id = prodlot_id, product_qty = product_qty, loc_id = loc_id, product_id=product_id, uom_id=uom_id, context = context)
        return self.eval_onchange_lot_date(cr, uid, res, prodlot_id)

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, address_id=False, prod_qty=0.0, prodlot_id=False):
        """Extends this event checking prodlot obtained"""
        res = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, address_id)

        return self.eval_onchange_lot_date(cr, uid, res)

    def onchange_location_id(self, cr, uid, ids, product_id = False, location_id = False, dummy = False, product_qty=False, product_uom_id=False):
        """event fires when changes the location, checks the location and return a default production lot for this location"""
        res = super(stock_move, self).onchange_location_id(cr, uid, ids,product_id,location_id,dummy,product_qty,product_uom_id)

        return self.eval_onchange_lot_date(cr, uid, res)

stock_move()