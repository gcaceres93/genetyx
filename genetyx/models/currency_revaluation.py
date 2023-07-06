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




_logger = logging.getLogger(__name__)


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


class account_move(models.Model):
    _inherit = 'account.move'

    
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




