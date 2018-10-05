# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = "res.partner"

    wallet = fields.Float(digits=(16, 0),
                          compute='_compute_wallet', string='Wallet amount', help='This wallet amount of customer')

    @api.multi
    def _compute_wallet(self):
        use_wallet_journal = self.env['account.journal'].sudo().search([
            ('use_wallet', '=', True), ('company_id', '=', self.env.user.company_id.id)])
        give_wallet_journal = self.env['account.journal'].sudo().search([
            ('give_wallet', '=', True), ('company_id', '=', self.env.user.company_id.id)])
        use_wallet_statements = self.env['account.bank.statement'].sudo().search(
            [('journal_id', 'in', [j.id for j in use_wallet_journal])])
        give_wallet_statements = self.env['account.bank.statement'].sudo().search(
            [('journal_id', 'in', [j.id for j in give_wallet_journal])])
        for partner in self:
            partner.wallet = 0
            _logger.info(partner.name)
            _logger.info(partner.id)
            if len(give_wallet_statements) > 0:
                self._cr.execute(
                    """SELECT l.partner_id, SUM(l.amount)
                    FROM account_bank_statement_line l
                    WHERE l.statement_id IN %s AND l.partner_id = %s
                    GROUP BY l.partner_id
                    """,
                    (tuple(give_wallet_statements.ids), partner.id))
                datas = self._cr.fetchall()
                for item in datas:
                    partner.wallet -= item[1]
                _logger.info(datas)
            if len(use_wallet_statements) > 0:
                self._cr.execute(
                    """SELECT l.partner_id, SUM(l.amount)
                    FROM account_bank_statement_line l
                    WHERE l.statement_id IN %s AND l.partner_id = %s
                    GROUP BY l.partner_id
                    """,
                    (tuple(use_wallet_statements.ids), partner.id))
                datas = self._cr.fetchall()
                _logger.info(datas)
                _logger.info('----------------- *** --------------------')
                for item in datas:
                    partner.wallet -= item[1]
