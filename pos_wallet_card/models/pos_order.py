# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class pos_order(models.Model):

    _inherit = "pos.order"

    def _prepare_bank_statement_line_payment_values(self, data):
        order_id = self.id
        datas = super(pos_order, self)._prepare_bank_statement_line_payment_values(data)
        journal_id = datas.get('journal_id')
        if journal_id and order_id and self.partner_id and self.partner_id.id != datas['partner_id']:
            journal = self.env['account.journal'].browse(journal_id)
            if journal['give_wallet'] or journal['use_wallet']:
                datas['partner_id'] = self.partner_id.id
        return datas

