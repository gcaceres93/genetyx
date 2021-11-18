# Copyright 2012-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError,ValidationError
from copy import deepcopy
import logging
import time
from datetime import date
from collections import OrderedDict, defaultdict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree





class AccountPartialReconciles(models.Model):
    _inherit = "account.partial.reconcile"


    @api.model
    def create_exchange_rate_entry(self, aml_to_fix, move):
        """
        Automatically create a journal items to book the exchange rate
        differences that can occur in multi-currencies environment. That
        new journal item will be made into the given `move` in the company
        `currency_exchange_journal_id`, and one of its journal items is
        matched with the other lines to balance the full reconciliation.

        :param aml_to_fix: recordset of account.move.line (possible several
            but sharing the same currency)
        :param move: account.move
        :return: tuple.
            [0]: account.move.line created to balance the `aml_to_fix`
            [1]: recordset of account.partial.reconcile created between the
                tuple first element and the `aml_to_fix`
        """
        partial_rec = self.env['account.partial.reconcile']
        aml_model = self.env['account.move.line']

        created_lines = self.env['account.move.line']
        for aml in aml_to_fix:
            # create the line that will compensate all the aml_to_fix

            if aml.amount_residual == 0:
                resi = 0
            else:
                resi = aml.amount_residual_currency and -aml.amount_residual_currency or 0.0
            if aml.partner_id:
                partner_id = aml.partner_id.id
            else:
                partner_id = False
            line_to_rec = aml_model.with_context(check_move_validity=False).create({
                'name': _('Currency exchange rate difference'),
                'debit': aml.amount_residual < 0 and -aml.amount_residual or 0.0,
                'credit': aml.amount_residual > 0 and aml.amount_residual or 0.0,
                'account_id': aml.account_id.id,
                'move_id': move.id,
                'currency_id': aml.currency_id.id,
                'amount_currency': resi,
                'partner_id': partner_id
            })

            # create the counterpart on exchange gain/loss account
            exchange_journal = move.company_id.currency_exchange_journal_id
            aml_model.with_context(check_move_validity=False).create({
                'name': _('Currency exchange rate difference'),
                'debit': aml.amount_residual > 0 and aml.amount_residual or 0.0,
                'credit': aml.amount_residual < 0 and -aml.amount_residual or 0.0,
                'account_id': aml.amount_residual > 0 and exchange_journal.default_debit_account_id.id or exchange_journal.default_credit_account_id.id,
                'move_id': move.id,
                'currency_id': aml.currency_id.id,
                'amount_currency': aml.amount_residual_currency and aml.amount_residual_currency or 0.0,
                'partner_id': partner_id
            })

            # reconcile all aml_to_fix
            partial_rec |= self.create(
                self._prepare_exchange_diff_partial_reconcile(
                    aml=aml,
                    line_to_reconcile=line_to_rec,
                    currency=aml.currency_id or False)
            )
            created_lines |= line_to_rec
        return created_lines, partial_rec

class WizardCurrencyRevaluation(models.TransientModel):

    _inherit = 'wizard.currency.revaluation'

    @api.multi
    def revaluate_currency(self):
        """
        Compute unrealized currency gain and loss and add entries to
        adjust balances

        @return: dict to open an Entries view filtered on generated move lines
        """

        account_obj = self.env['account.account']

        company = self.journal_id.company_id or self.env.user.company_id
        if self._check_company(company):
            raise UserError(
                _("No revaluation or provision account are defined"
                  " for your company.\n"
                  "You must specify at least one provision account or"
                  " a couple of provision account in the accounting settings.")
            )
        created_ids = []
        # Search for accounts Balance Sheet to be revaluated
        # on those criteria
        # - deferral method of account type is not None
        account_ids = account_obj.search([
            ('user_type_id.include_initial_balance', '=', 'True'),
            ('currency_revaluation', '=', True), ('currency_id','!=',False) ])

        if not account_ids:
            raise UserError(
                _("No account to be revaluated found. "
                  "Please check 'Allow Currency Revaluation' "
                  "for at least one account in account form.")
            )

        # Get balance sums
        account_sums = account_ids.compute_revaluations(self.revaluation_date)

        for account_id, account_tree in account_sums.items():
            for partner_id, partner_tree in account_tree.items():
                for currency_id, sums in partner_tree.items():
                    # Update sums with compute amount currency balance
                    diff_balances = self._compute_unrealized_currency_gl(
                        currency_id,
                        sums
                    )
                    account_sums[account_id][partner_id][currency_id]. \
                        update(diff_balances)

        # Create entries only after all computation have been done
        for account_id, account_tree in account_sums.items():
            for partner_id, partner_tree in account_tree.items():
                for currency_id, sums in partner_tree.items():
                    adj_balance = sums.get('unrealized_gain_loss', 0.0)
                    if not adj_balance:
                        continue
                    account_type = account_obj.browse(account_id).internal_type
                    if account_type not in ['receivable', 'payable']:
                        partner_id = None
                    rate = sums.get('currency_rate', 0.0)
                    label = self._format_label(
                        self.label, account_id, currency_id, rate
                    )

                    # Write an entry to adjust balance
                    new_ids = self._write_adjust_balance(
                        account_id,
                        currency_id,
                        partner_id,
                        adj_balance,
                        label,
                        self,
                        sums
                    )
                    created_ids.extend(new_ids)

        cuentas = account_ids.mapped('id')
        account_move_line = self.env['account.move.line'].search(
            [('date', '<=', self.revaluation_date), ('move_id.state', '=', 'posted'), ('account_id', 'in', (cuentas))])
        moneda = None
        tasa = 1
        for cuen in account_ids:
            dife=0
            suma=sum(account_move_line.filtered(lambda r:r.account_id==cuen and r.amount_currency != 0).mapped('amount_currency'))

            if suma != 0:
                if moneda:
                    if moneda != cuen.currency_id:
                        moneda = cuen.currency_id
                        tasa = self.env['res.currency.rate'].search(
                            [('name', '=', self.revaluation_date), ('company_id', '=', self.env.user.company_id.id),
                             ('currency_id', '=', moneda.id)])
                        # print(tasa)
                else:
                    moneda = cuen.currency_id
                    tasa = self.env['res.currency.rate'].search(
                        [('name', '=', self.revaluation_date), ('company_id', '=', self.env.user.company_id.id),
                         ('currency_id', '=', moneda.id)])
                total_cambio = suma * tasa.set_venta
                suma_con_diferencia = sum(account_move_line.filtered(lambda r:r.account_id==cuen and r.balance != 0).mapped('balance'))

                dife = total_cambio - suma_con_diferencia
                if dife != 0:
                    label = self._format_label(
                        self.label, cuen.id, moneda.id, tasa.rate
                    )

                    # Write an entry to adjust balance
                    sums = {'foreign_balance': 0,
                    'balance': 0,
                    'revaluated_balance': 0,
                    'currency_rate':0}
                    new_ids = self._write_adjust_balance(
                        cuen.id,
                        moneda.id,
                        None,
                        dife,
                        label,
                        self,
                        sums
                    )
                    created_ids.extend(new_ids)
                    print('dife %s cuenta %s suma %s new_ids %s' % (dife,cuen.name,suma,new_ids))
            else:
                balance = sum(account_move_line.filtered(lambda r:r.account_id==cuen and r.amount_currency != 0).mapped('balance'))
                if balance != 0:
                    asientos = self.env['account.move.line'].browse(created_ids)
                    moveasi= asientos.filtered(lambda r:r.account_id == cuen)
                    if moveasi:
                        if len(moveasi)==1:
                            moveasi.move_id.button_cancel()
                            difere= abs(balance) - abs(moveasi.balance)
                            if difere > 0:
                                #sumas= difere + moveasi.balance
                                if balance < 0:
                                    if moveasi.debit > 0 :
                                        ii=moveasi.move_id.line_ids.filtered(lambda r:r.credit>0)


                                        moveasi.with_context(check_move_validity=False).debit = 0
                                        ii.with_context(check_move_validity=False).credit = 0

                                        ii.with_context(check_move_validity=False).credit = abs(balance)
                                        moveasi.with_context(check_move_validity=False).debit = abs(balance)
                                        moveasi.with_context(check_move_validity=False).balance = balance
                                        ii.with_context(check_move_validity=False).balance = balance
                                    else:
                                        # revaluation_loss_account_id
                                        # revaluation_gain_account_id

                                        moveasi.with_context(check_move_validity=False).debit = 0
                                        ii.with_context(check_move_validity=False).credit = 0

                                        moveasi.with_context(check_move_validity=False).credit = abs(balance)
                                        moveasi.with_context(check_move_validity=False).account_id = self.env.user.company_id.revaluation_gain_account_id
                                        ii.with_context(check_move_validity=False).debit = abs(balance)
                                        moveasi.with_context(check_move_validity=False).balance = balance
                                        ii.with_context(check_move_validity=False).balance = balance
                                elif balance > 0 :
                                    if moveasi.credit > 0:
                                        ii = moveasi.move_id.line_ids.filtered(lambda r: r.credit > 0)

                                        moveasi.with_context(check_move_validity=False).debit = 0
                                        ii.with_context(check_move_validity=False).credit = 0

                                        moveasi.with_context(check_move_validity=False).credit = abs(balance)
                                        ii.with_context(check_move_validity=False).debit = abs(balance)
                                        moveasi.with_context(check_move_validity=False).balance = balance
                                        ii.with_context(check_move_validity=False).balance = balance
                                    else:
                                        # revaluation_loss_account_id
                                        # revaluation_gain_account_id

                                        moveasi.with_context(check_move_validity=False).debit = 0
                                        ii.with_context(check_move_validity=False).credit = 0

                                        moveasi.with_context(check_move_validity=False).credit = abs(balance)
                                        moveasi.with_context(
                                            check_move_validity=False).account_id = self.env.user.company_id.revaluation_loss_account_id
                                        ii.with_context(check_move_validity=False).debit = abs(balance)
                                        moveasi.with_context(check_move_validity=False).balance = balance
                                        ii.with_context(check_move_validity=False).balance = balance
                            moveasi.move_id.post()
                            # elif difere < 0:



                # print('created_ids')
                # print(created_ids)



            # print('cuenta %s suma %s' %(cuen.name,suma))
        # raise ValidationError('test')
        if created_ids:
            return {'domain': "[('id', 'in', %s)]" % created_ids,
                    'name': _("Created revaluation lines"),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'auto_search': True,
                    'res_model': 'account.move.line',
                    'view_id': False,
                    'search_view_id': False,
                    'type': 'ir.actions.act_window'}
        else:
            raise UserError(
                _("No accounting entry has been posted.")
            )

class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.multi
    def _revaluation_query(self, revaluation_date):
        tables, where_clause, where_clause_params = \
            self.env['account.move.line']._query_get()

        query = ("with amount as ( SELECT aml.account_id, aml.partner_id, "
                 "(select aa.currency_id from account_account aa where aa.id=aml.account_id) as currency_id, aml.debit, aml.credit, aml.amount_currency "
                 "FROM account_move_line aml LEFT JOIN "
                 "account_partial_reconcile aprc ON (aml.balance < 0 "
                 "AND aml.id = aprc.credit_move_id) LEFT JOIN "
                 "account_move_line amlcf ON (aml.balance < 0 "
                 "AND aprc.debit_move_id = amlcf.id "
                 "AND amlcf.date < %s ) LEFT JOIN "
                 "account_partial_reconcile aprd ON (aml.balance > 0 "
                 "AND aml.id = aprd.debit_move_id) LEFT JOIN "
                 "account_move_line amldf ON (aml.balance > 0 "
                 "AND aprd.credit_move_id = amldf.id "
                 "AND amldf.date < %s ) "
                 "WHERE aml.account_id IN %s "
                 "AND aml.date <= %s "
                 "AND aml.currency_id IS NOT NULL "
                 "GROUP BY aml.id "
                 "HAVING (select amm.id from account_move amm where amm.date<= %s and amm.id in (select fri.exchange_move_id from account_full_reconcile fri where fri.id = aml.full_reconcile_id )) IS NULL "
                 "OR (MAX(amldf.id) IS NULL AND MAX(amlcf.id) IS NULL)"
                 ") SELECT account_id as id, partner_id, currency_id, " +
                 ', '.join(self._sql_mapping.values()) +
                 " FROM amount " +
                 (("WHERE " + where_clause) if where_clause else " ") +
                 " GROUP BY account_id, currency_id, partner_id")
        # query = ("with amount as ( SELECT aml.account_id, aml.partner_id, "
        #          "(select aa.currency_id from account_account aa where aa.id=aml.account_id) as currency_id, aml.debit, aml.credit, aml.amount_currency "
        #          "FROM account_move_line aml LEFT JOIN "
        #          "account_partial_reconcile aprc ON (aml.balance < 0 "
        #          "AND aml.id = aprc.credit_move_id) LEFT JOIN "
        #          "account_move_line amlcf ON (aml.balance < 0 "
        #          "AND aprc.debit_move_id = amlcf.id "
        #          "AND amlcf.date < %s ) LEFT JOIN "
        #          "account_partial_reconcile aprd ON (aml.balance > 0 "
        #          "AND aml.id = aprd.debit_move_id) LEFT JOIN "
        #          "account_move_line amldf ON (aml.balance > 0 "
        #          "AND aprd.credit_move_id = amldf.id "
        #          "AND amldf.date < %s ) "
        #          "WHERE aml.account_id IN %s "
        #          "AND aml.date <= %s "
        #          "AND aml.currency_id IS NOT NULL "
        #          "GROUP BY aml.id "
        #          "HAVING aml.full_reconcile_id IS NULL "
        #          "OR (MAX(amldf.id) IS NULL AND MAX(amlcf.id) IS NULL)"
        #          ") SELECT account_id as id, partner_id, currency_id, " +
        #          ', '.join(self._sql_mapping.values()) +
        #          " FROM amount " +
        #          (("WHERE " + where_clause) if where_clause else " ") +
        #          " GROUP BY account_id, currency_id, partner_id")

        params = []
        params.append(revaluation_date)
        params.append(revaluation_date)
        params.append(tuple(self.ids))
        params.append(revaluation_date)
        params.append(revaluation_date)
        params += where_clause_params
        # print('------')
        # print(query)
        # print('------')
        # print(params)
        # raise ValidationError ('query')
        return query, params

class account_move(models.Model):
    _inherit = 'account.move'

    @api.multi
    def setear_nombre(self):
        asientos_1 = self.env['account.move'].search([('state','=','posted'),('journal_id','=',self.env.user.company_id.currency_exchange_journal_id.id)])
        asientos = asientos_1.filtered(lambda r: not r.ref)
        for asie in asientos:

            for rec in asie:
                if not rec.ref and rec.journal_id == rec.env.user.company_id.currency_exchange_journal_id:
                    lineas_recon = rec.line_ids.filtered(lambda r: r.full_reconcile_id )
                    for lineas in lineas_recon:
                        linea_pago = self.env['account.move.line'].search([('full_reconcile_id','=',lineas.full_reconcile_id.id),('payment_id','!=',False)])
                        for lp in linea_pago:
                            print('pagos lineas %s %s' % (lp.ref or lp.name,lineas.move_id))
                            lineas.move_id.write({'ref':lp.ref or lp.name})



    # @api.model
    # def _run_reverses_entries(self):
    #     ''' This method is called from a cron job. '''
    #     records = self.search([
    #         # ('state', '=', 'posted'),
    #         ('auto_reverse', '=', True),
    #         ('reverse_date', '<=', fields.Date.today()),
    #         ('reverse_entry_id', '=', False)])
    #     for move in records:
    #         date = None
    #         company = move.company_id or self.env.user.company_id
    #         if move.reverse_date and (not company.period_lock_date or move.reverse_date > company.period_lock_date):
    #             date = move.reverse_date
    #         move.reverse_moves(date=date, auto=True)
    #         move.button_cancel()

class WizardCurrencyRevaluations(models.TransientModel):

    _inherit = 'wizard.currency.revaluation'

    @api.model
    def _format_label(self, text, account_id, currency_id, rate):
        """
        Return a text with replaced keywords by values

        @param str text: label template, can use
            %(account)s, %(currency)s, %(rate)s
        @param int account_id: id of the account to display in label
        @param int currency_id: id of the currency to display
        @param float rate: rate to display
        """
        account_obj = self.env['account.account']
        currency_obj = self.env['res.currency']

        account = account_obj.browse(account_id)
        currency = currency_obj.browse(currency_id)
        tasa = self.env['res.currency.rate'].search([('currency_id', '=', currency_id), ('rate', '=', rate)], limit=1)

        # data = {'account': account.code or False,
        #         'currency': currency.name or False,
        #         'rate': rate}
        data = {'account': account.code or False,
                'currency': currency.name or False,
                'rate': tasa.set_venta}
        return text % data



    def _create_move_and_lines(
            self, amount, debit_account_id, credit_account_id,
            sums, label, form, partner_id, currency_id,
            analytic_debit_acc_id=False, analytic_credit_acc_id=False):

        base_move = {
            'journal_id': form.journal_id.id,
            'date': form.revaluation_date,
        }
        if form.journal_id.company_id.reversable_revaluations:
            base_move['auto_reverse'] = True
            base_move['reverse_date'] = form.revaluation_date + timedelta(
                days=1)

        base_line = {
            'name': label,
            'partner_id': partner_id,
            'currency_id': currency_id,
            'amount_currency': 0.0,
            'date': form.revaluation_date
        }

        base_line['gl_foreign_balance'] = sums.get('foreign_balance', 0.0)
        base_line['gl_balance'] = sums.get('balance', 0.0)
        base_line['gl_revaluated_balance'] = sums.get(
            'revaluated_balance', 0.0)
        base_line['gl_currency_rate'] = sums.get('currency_rate', 0.0)

        debit_line = base_line.copy()
        credit_line = base_line.copy()

        debit_line.update({
            'debit': amount,
            'credit': 0.0,
            'account_id': debit_account_id,
        })

        if analytic_debit_acc_id:
            credit_line.update({
                'analytic_account_id': analytic_debit_acc_id,
            })

        credit_line.update({
            'debit': 0.0,
            'credit': amount,
            'account_id': credit_account_id,
        })

        if analytic_credit_acc_id:
            credit_line.update({
                'analytic_account_id': analytic_credit_acc_id,
            })
        base_move['line_ids'] = [(0, 0, debit_line), (0, 0, credit_line)]
        created_move = self.env['account.move'].create(base_move)
        created_move.post()

        return [x.id for x in created_move.line_ids]

