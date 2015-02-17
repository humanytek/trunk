from osv import osv, fields
from datetime import datetime
from tools.translate import _
import time

class stock_lot_config(osv.osv):
    """This model contains configure data which will be used in production lot."""
    _name = "stock.lot.config"
    _columns={
            'name':fields.char('Name',size=64,required=True),
            'required':fields.boolean('Required'),
            'indexed':fields.boolean('Indexed')
              }
    _defaults = {
            'required':lambda *a:True,
                 }
stock_lot_config()


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    def _get_if_expired(self, cr, uid, ids, field_name, arg, context=None):
        """get if prodlots is expired based on due_date in lot control"""
        if context is None: context = {}
        res = {}
        for obj_prodlot_id in self.browse(cr, uid, ids):
            value = False
            for lot_control_obj in obj_prodlot_id.control_ids:

                #check if prodlot is expired

                if lot_control_obj.due_date and datetime.strptime(lot_control_obj.due_date, "%Y-%m-%d %H:%M:%S") < datetime.now():
                    value = True
            res[obj_prodlot_id.id] = value

        return res

    _columns = {
        'expired': fields.function(_get_if_expired, method=True, type="boolean", string="Expired",
            store={'stock.production.lot': (lambda self, cr, uid, ids, c={}: ids, None, 20)}),

        'control_ids':fields.one2many('stock.lot.control','prodlot_id','Traceable Data'),
        'name': fields.char('Production Lot/Part Number', size=64, required=True, help="Unique production lot, will be displayed as: PREFIX/SERIAL [INT_REF]"),

        'control_number': fields.related('control_ids', 'control_number', type='char', size=64, string='Control Number'),
        'lot_config_id': fields.related('control_ids', 'lot_config_id', type='many2one', relation='stock.lot.config', string='Lot Config. Data'),
    }

    _sql_constraints = [
        ('name_ref_uniq', 'unique (name)', 'The Production Lot/Part Number must be unique !'),
    ]

stock_production_lot()

class stock_control_lot(osv.osv):
    _name="stock.lot.control"
    _rec_name = 'lot_config_id'
    _columns={
            'lot_config_id': fields.many2one('stock.lot.config','Name Data'),
            'control_number':fields.char('Control Number', size=128),
            'expirable':fields.boolean('Expirable'),
            'due_date': fields.datetime('Expiry Date',help='The date on which the lot should be removed.'),
            'required':fields.related('lot_config_id','required',type='boolean',string="Required"),
            'indexed':fields.related('lot_config_id','indexed',type='boolean',string="Indexed"),
            'prodlot_id':fields.many2one('stock.production.lot','Production Lot')
              }
    _defaults = {
            'expirable':lambda *a:False,
                }
    def _check_indexed_control_num(self, cr, uid, ids, context=None):
        ctrl = self.browse(cr,uid,ids[0])
        ctrl_num = ctrl.control_number
        #lot_id = ctrl.prodlot_id.id #ctrl_obj.prodlot_id.id <> lot_id and
        ctrl_ids = self.search(cr,uid,[('id','not in',ids)])
        for ctrl_obj in self.browse(cr, uid, ctrl_ids, context=context):
            if ctrl_obj.indexed and ctrl_obj.control_number ==  ctrl_num:
                return False
        return True

    _constraints = [
                (_check_indexed_control_num, _('Another production lot already exists with this control number !'), ['control_number']),
                ]

    def onchange_expirable(self, cr, uid, ids, expirable,context=None):
        if expirable:return {'value':{'due_date':time.strftime('%Y-%m-%d %H:%M:%S'), }}
        else: return {'value':{'due_date':False}}

    def onchange_lot_config_id(self,cr,uid,ids,lot_config_id):
        res={}
        if not lot_config_id:
            res['required']=False
            res['indexed']=False
            return {'value':res
                    }
        else:
            lot_config_obj = self.pool.get('stock.lot.config').browse(cr,uid,lot_config_id,context=None)
            res['required'] = lot_config_obj.required
            res['indexed'] = lot_config_obj.indexed

        return {'value':res}
stock_control_lot()


