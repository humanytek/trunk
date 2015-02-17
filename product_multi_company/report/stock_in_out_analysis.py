# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 ZestyBeanz Technologies Pvt. Ltd.
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

from osv import osv
import tools

class report_mrp_inout(osv.osv):
    _inherit = 'report.mrp.inout'
    
    def init(self, cr):
        cr.execute("""
            create or replace view report_mrp_inout as (
                select
                    min(sm.id) as id,
                    to_char(sm.date,'YYYY:IW') as date,
                    sum(case when (sl.usage='internal') then
                        0.00 * sm.product_qty
                    else
                        0.0
                    end - case when (sl2.usage='internal') then
                        0.00 * sm.product_qty
                    else
                        0.0
                    end) as value
                from
                    stock_move sm
                left join product_product pp
                    on (pp.id = sm.product_id)
                left join product_template pt
                    on (pt.id = pp.product_tmpl_id)
                left join stock_location sl
                    on ( sl.id = sm.location_id)
                left join stock_location sl2
                    on ( sl2.id = sm.location_dest_id)
                where
                    sm.state in ('waiting','confirmed','assigned')
                group by
                    to_char(sm.date,'YYYY:IW')
            )""")

report_mrp_inout()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
