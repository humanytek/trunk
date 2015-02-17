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
import tools
import pooler

class template_agreement(osv.osv):
    _name = 'template.agreement'
    _columns = {
                'name' : fields.char('Name',size=64),
                'notes' : fields.text('Special Agreement Content'),
                'model_object_field':fields.many2one('ir.model.fields',string="Field",store=False),
                'sub_object':fields.many2one(
                 'ir.model',
                 'Sub-model',
                 help='When a relation field is used this field'
                 ' will show you the type of field you have selected',
                 store=False),
                'sub_model_object_field':fields.many2one(
                 'ir.model.fields',
                 'Sub Field',
                 help="When you choose relationship fields "
                 "this field will specify the sub value you can use.",
                 store=False),
                'copyvalue':fields.char('Expression',size=100,help="Copy and paste the value in the "
                "location you want to use a system value.", store=False),
                'null_value':fields.char(
                 'Null Value',
                 help="This Value is used if the field is empty",
                 size=50, store=False),

                }
    def change_model(self, cr, uid, ids, object_name, context=None):
        if object_name:
            mod_name = self.pool.get('ir.model').read(
                                              cursor,
                                              user,
                                              object_name,
                                              ['model'], context)['model']
        else:
            mod_name = False
        return {
                'value':{'model_int_name':mod_name}
                }

    def build_expression(self, field_name, sub_field_name, null_value):
        """
        Returns a template expression based on data provided
        @param field_name: field name
        @param sub_field_name: sub field name (M2O)
        @param null_value: default value if the target value is empty
        @param template_language: name of template engine
        @return: computed expression
        """

        expression = ''
        if field_name:
                expression = "${object." + field_name
                if sub_field_name:
                    expression += "." + sub_field_name
                if null_value:
                    expression += " or '''%s'''" % null_value
                expression += "}"
        return expression

    def onchange_model_object_field(self, cr, uid, ids, model_object_field, context=None):
        if not model_object_field:
            return {}
        result = {}
        field_obj = self.pool.get('ir.model.fields').browse(cr, uid, model_object_field, context)
        if field_obj.ttype in ['many2one', 'one2many', 'many2many']:
            res_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', field_obj.relation)], context=context)
            if res_ids:
                result['sub_object'] = res_ids[0]
                result['copyvalue'] = self.build_expression(False,
                                                      False,
                                                      False,
                                                      )
                result['sub_model_object_field'] = False
                result['null_value'] = False
        else:
            result['sub_object'] = False
            result['copyvalue'] = self.build_expression(field_obj.name,
                                                  False,
                                                  False,
                                                  )
            result['sub_model_object_field'] = False
            result['null_value'] = False
        return {'value':result}

    def onchange_sub_model_object_field(self, cr, uid, ids, model_object_field, sub_model_object_field, context=None):
        if not model_object_field or not sub_model_object_field:
            return {}
        result = {}
        field_obj = self.pool.get('ir.model.fields').browse(cr, uid, model_object_field, context)
        if field_obj.ttype in ['many2one', 'one2many', 'many2many']:
            res_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', field_obj.relation)], context=context)
            sub_field_obj = self.pool.get('ir.model.fields').browse(cr, uid, sub_model_object_field, context)
            if res_ids:
                result['sub_object'] = res_ids[0]
                result['copyvalue'] = self.build_expression(field_obj.name,
                                                      sub_field_obj.name,
                                                      False,

                                                      )
                result['sub_model_object_field'] = sub_model_object_field
                result['null_value'] = False
        else:
            result['sub_object'] = False
            result['copyvalue'] = self.build_expression(field_obj.name,
                                                  False,
                                                  False,
                                                  )
            result['sub_model_object_field'] = False
            result['null_value'] = False
        return {'value':result}

    def onchange_null_value(self, cr, uid, ids, model_object_field, sub_model_object_field, null_value, context=None):
        if not model_object_field and not null_value:
            return {}
        result = {}
        field_obj = self.pool.get('ir.model.fields').browse(cr, uid, model_object_field, context)
        if field_obj.ttype in ['many2one', 'one2many', 'many2many']:
            res_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', field_obj.relation)], context=context)
            sub_field_obj = self.pool.get('ir.model.fields').browse(cr, uid, sub_model_object_field, context)
            if res_ids:
                result['sub_object'] = res_ids[0]
                result['copyvalue'] = self.build_expression(field_obj.name,
                                                      sub_field_obj.name,
                                                      null_value,
                                                      )
                result['sub_model_object_field'] = sub_model_object_field
                result['null_value'] = null_value
        else:
            result['sub_object'] = False
            result['copyvalue'] = self.build_expression(field_obj.name,
                                                  False,
                                                  null_value,

                                                  )
            result['sub_model_object_field'] = False
            result['null_value'] = null_value
        return {'value':result}
template_agreement()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: