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

from osv import fields, osv

class account_cost_center(osv.osv):
    _name = 'account.cost.center'
    _description = """ Creates a Cost center configurator"""   
    _columns = {
                "name": fields.char("Name", size=64, required=True),
                "active": fields.boolean("Active"),
                "journal_ids": fields.one2many("account.journal", "account_cost_id", "Journals",)
                }
    
    _defaults = {
                 'active': True
                 }
    
account_cost_center()

class account_journal(osv.osv):
    _inherit = "account.journal"  
    _description = """ Add a new many2one field related to model account.cost.center"""
    _columns = {
                "account_cost_id": fields.many2one("account.cost.center", "Cost Id")
               }
account_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: