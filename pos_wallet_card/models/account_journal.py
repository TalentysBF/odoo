# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class account_journal(models.Model):

    _inherit = "account.journal"

    use_wallet = fields.Boolean('Use Wallet', help='This is account journal management customers use wallet money')
    give_wallet = fields.Boolean('Give Wallet', help='This is account journal give customers money charge')

    @api.onchange('use_wallet')
    def on_change_staff_level(self):
        if self.use_wallet and self.use_wallet == True:
            self.give_wallet = False

    @api.onchange('give_wallet')
    def on_change_staff_level(self):
        if self.give_wallet and self.give_wallet == True:
            self.use_wallet = False

