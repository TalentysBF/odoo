# -*- coding:utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    test = fields.Char('TEST')

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=False,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    number = fields.Char(related='move_id.name', store=True, readonly=False, copy=False)
