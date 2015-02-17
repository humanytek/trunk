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

from osv import osv

class account_mx_report_data_wizard(osv.osv_memory):
    _inherit = 'account.mx_report_data_wizard'
    
    def get_info(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        if context is None:
            context = {}
        res = super(account_mx_report_data_wizard, self).get_info(cr, uid, ids, context=context)
        data = context and context.get('active_ids', []) or []

        for params in self.browse(cr, uid, ids, context=context):
            cr.execute("""
                
                drop function if exists f_get_journal_id_from_cost_center(report_id integer);
                
                CREATE OR REPLACE FUNCTION f_get_journal_id_from_cost_center
                (report_id integer)
                RETURNS TABLE(id integer) AS
                $$
                
                select id from account_journal where account_cost_id in
                (select cost_center_id from mx_report_cost_center where report_id = report_id)
                
                $$ LANGUAGE 'sql';
                
                drop function if exists f_get_mx_report_data_detail
                (x_report_id integer, x_period_id integer, x_uid integer, x_parent_id integer, x_parent_group varchar(64));


                CREATE OR REPLACE FUNCTION f_get_mx_report_data_detail
                (x_report_id integer, x_period_id integer, x_uid integer, x_parent_id integer, x_parent_group varchar(64))
                RETURNS TABLE
                (
                create_uid integer,
                create_date timestamp,
                write_date timestamp,
                write_uid integer,
                report_id integer,
                report_group varchar(64),
                report_section varchar(64),
                sequence integer,
                report_sign float,
                account_sign float,
                account_code varchar(64),
                account_name varchar(128),
                period_id integer,
                initial_balance float,
                debit float, 
                credit float) 
                AS
                $BODY$
                BEGIN
                    return query 
                    select 
                        x_uid, LOCALTIMESTAMP, LOCALTIMESTAMP, x_uid,
                        subreport.parent_id,
                        case char_length(x_parent_group) 
                        when 0 then subreport.internal_group 
                        else x_parent_group
                        end,
                        subreport.name,
                        subreport.sequence,
                        case subreport.sign
                        when 'positive' then 1.0
                        else -1.0
                        end::float,
                        account_type.sign::float, 
                        account.code, 
                        account.name, 
                        period.id,
                        case date_part('month', period.date_start)
                        when 1 then 
                            account_type.sign * 
                            (select COALESCE(sum(line.debit), 0.00) -  COALESCE(sum(line.credit), 0.00)
                            from account_move_line line, account_journal journal
                            where line.state='valid' and line.account_id in (select f_account_child_ids(account.id))
                            and (line.journal_id = journal.id and journal.type='situation'
                            and line.journal_id in (select aj.id from account_journal aj where aj.account_cost_id in
                (select mx.cost_center_id from mx_report_cost_center mx where mx.report_id = subreport.id)))
                            and line.period_id = period.id
                            )
                        else
                            account_type.sign * 
                            (select COALESCE(sum(line.debit), 0.00) -  COALESCE(sum(line.credit), 0.00)
                            from account_move_line line, account_journal journal
                            where line.state='valid' and line.account_id in (select f_account_child_ids(account.id))
                            and (line.journal_id = journal.id
                            and line.journal_id in (select aj.id from account_journal aj where aj.account_cost_id in
                (select mx.cost_center_id from mx_report_cost_center mx where mx.report_id = subreport.id))) 
                            and line.period_id in 
                                (select xperiodo.id from account_period xperiodo 
                                where xperiodo.fiscalyear_id= (select fiscalyear.id from account_fiscalyear fiscalyear where period.fiscalyear_id = fiscalyear.id)
                                and xperiodo.name < period.name 
                                )
                            )
                        end::float,
                        (select COALESCE(sum(line.debit), 0.00) 
                        from account_move_line line, account_journal journal
                        where line.state='valid' and line.account_id in (select f_account_child_ids(account.id))
                        and (line.journal_id = journal.id and journal.type<>'situation'
                        and line.journal_id in (select aj.id from account_journal aj where aj.account_cost_id in
                (select mx.cost_center_id from mx_report_cost_center mx where mx.report_id = subreport.id)))
                        and line.period_id = period.id)::float
                        ,
                        (select COALESCE(sum(line.credit), 0.00) 
                        from account_move_line line, account_journal journal
                        where line.state='valid' and line.account_id in (select f_account_child_ids(account.id))
                        and (line.journal_id = journal.id and journal.type<>'situation'
                        and line.journal_id in (select aj.id from account_journal aj where aj.account_cost_id in
                (select mx.cost_center_id from mx_report_cost_center mx where mx.report_id = subreport.id)))
                        and line.period_id = period.id)::float
                        
                        from account_period period, 
                        account_mx_report_definition subreport 
                            left join account_account_mx_reports_rel subreport_accounts on subreport_accounts.mx_report_definition_id = subreport.id
                            left join account_account account on subreport_accounts.account_id = account.id
                            left join account_account_type account_type on account.user_type=account_type.id    
                        where period.id=x_period_id and
                        case x_parent_id 
                        when 0 then subreport.id = x_report_id
                        else subreport.parent_id = x_parent_id
                        end
                        order by subreport.parent_id, subreport.sequence, account.code;
                END
                $BODY$
                LANGUAGE 'plpgsql';
                --select * from f_get_mx_report_data_detail(14, 24, 1, 2)
                drop function if exists f_get_mx_report_data
                (x_report_id integer, x_period_id integer, x_uid integer);
                CREATE OR REPLACE FUNCTION f_get_mx_report_data
                (x_report_id integer, x_period_id integer, x_uid integer)
                RETURNS boolean 
                AS
                $BODY$
                DECLARE
                _cursor CURSOR FOR 
                    SELECT _a.id, _a.report_id, _a.parent_id, _a.name as report_section, case _a.sign when 'positive' then 1.0::float else -1.00::float end sign,
                    _a.sequence, _a.report_id_use_resume, _a.report_id_account, _a.report_id_label, _a.report_id_show_result, _a.internal_group        
                    from account_mx_report_definition _a 
                        where _a.parent_id = x_report_id 
                        order by _a.sequence;
                _result record;
                BEGIN
                    delete from account_mx_report_data;    
                    FOR _record IN _cursor
                    LOOP
                        insert into account_mx_report_data
                        (
                            create_uid, create_date, write_date, write_uid,
                        report_id, report_group, report_section, sequence, report_sign, account_sign, 
                        account_code, account_name, --account_id, 
                        period_id, 
                        initial_balance, debit, credit, ending_balance, debit_credit_ending_balance
                            )
                        select 
                        create_uid, create_date, write_date, write_uid,
                        report_id, report_group, report_section, sequence, report_sign, account_sign, 
                        account_code, account_name, --account_id, 
                        period_id, 
                        initial_balance, debit, credit,
                        (initial_balance  + account_sign * (debit - credit)) ending_balance,
                        (account_sign * (debit - credit)) debit_credit_ending_balance
                        from f_get_mx_report_data_detail(_record.id, x_period_id, x_uid, 0, '');
                        IF _record.report_id is not null THEN
                            --RAISE NOTICE 'Hay un subreporte para % y la casilla resumido está en %', _record.report_section, _record.report_id_use_resume;
                            IF not _record.report_id_use_resume THEN
                                --RAISE NOTICE 'Entramos a generar el detalle del subreporte';
                                insert into account_mx_report_data
                                (
                                create_uid, create_date, write_date, write_uid,
                                report_id, report_group, report_section, sequence, report_sign, account_sign, 
                                account_code, account_name, --account_id, 
                                period_id, 
                                initial_balance, debit, credit, ending_balance, debit_credit_ending_balance
                                )
                                select 
                                create_uid, create_date, write_date, write_uid,
                                report_id, report_group, report_section, sequence, report_sign, account_sign, 
                                account_code, account_name, --account_id, 
                                period_id, 
                                initial_balance, debit, credit,
                                (initial_balance  + account_sign * (debit - credit)) ending_balance,
                                (account_sign * (debit - credit)) debit_credit_ending_balance                
                                from f_get_mx_report_data_detail(0, x_period_id, x_uid, _record.report_id, _record.internal_group);
                            ELSE
                                --RAISE NOTICE 'Generando solo el resultado del subreporte';
                                insert into account_mx_report_data
                                (
                                create_uid, create_date, write_date, write_uid,
                                report_id, report_group, report_section, sequence, report_sign, account_sign, 
                                account_code, account_name, --account_id, 
                                period_id, 
                                initial_balance, debit, credit, ending_balance, debit_credit_ending_balance
                                )
                                select 
                                create_uid, create_date, write_date, write_uid,
                                _record.parent_id as report_id, report_group, _record.report_section report_section, _record.sequence as sequence, _record.sign as report_sign, 1 as account_sign, 
                                _record.report_id_account::varchar(64) as account_code, _record.report_id_label::varchar(64) as account_name, period_id, 
                                --sum(initial_balance) initial_balance, sum(debit) debit, sum(credit) credit,
                        sum(initial_balance * report_sign) as initial_balance, 0.0::float as debit, 0.0::float as credit,
                                sum(report_sign * (initial_balance  + account_sign * (debit - credit))) ending_balance,
                                sum(report_sign * account_sign * (debit - credit)) debit_credit_ending_balance
                                from f_get_mx_report_data_detail(0, x_period_id, x_uid, _record.report_id, _record.internal_group)
                                group by 
                                create_uid, create_date, write_date, write_uid,
                                report_id, report_group, period_id;            
                            END IF;
                        END IF;
                    END LOOP;
                    return true;
                END
                $BODY$
                LANGUAGE 'plpgsql';
                select * from f_get_mx_report_data(""" + str(params.report_id.id) + "," + str(params.period_id.id) + "," +  str(uid) + ")")
            data = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not data[0]:
                raise osv.except_osv(
                        _('Error en script!'),
                        _('No se pudo generar la informacion para este reporte, por favor verifique su configuracion y vuelva a intentarlo'))
            values = self.pool.get('account.mx_report_data').search(cr, uid, [('id', '!=', 0)])
            value = {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'ht_reportes_contables_pdf' if params.report_type == 'pdf' else 'ht_reportes_contables_xls',
                'datas'         : {
                                    'model' : 'account.mx_report_data',
                                    'ids'   : values,
                                    }
                    } 

        return value

account_mx_report_data_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
