# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.tools import Number_To_Word


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('origin')
    def _getSaleOrder(self):
        if self.origin:
            sale_order = self.env['sale.order'].search([('name', '=', self.origin)])
            if sale_order:
                self.saleOrder_id = sale_order

    @api.depends('saleOrder_id')
    def _computeSaleOrder(self):
        return True

    @api.multi
    @api.depends('invoice_line_ids')
    def _get_amount_discount_total(self):
        self.ensure_one()
        res = {}
        total = 0.0
        for line in self.invoice_line_ids:
            if line.discount:
                temp = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * line.quantity
                total += temp
        return total

    @api.multi
    @api.depends('amount_total')
    def _get_amount_total_to_letter(self):
        self.ensure_one()
        amount_total_letter = ''
        if self.amount_total:
            amount_total_letter = Number_To_Word.Number_To_Word(self.amount_total, 'fr', self.currency_id.symbol, '')
        return amount_total_letter

    @api.multi
    @api.depends('saleOrder_id')
    def _get_all_calcul(self):
        self.ensure_one()
        res = {}
        if self.saleOrder_id and self.type_facture not in ('normal', 'avoir'):
            return 0.0

    saleOrder_id = fields.Many2one('sale.order', 'Vente', required=False, store=False, compute=_getSaleOrder)
    type_facture = fields.Selection([('acompte', 'Acompte'), ('acompte_exo', 'Acompte exonéré'), ('solde', 'Solde 1'),
                                     ('solde2', 'Solde 2'), ('solde_exo', 'Solde exonéré'),
                                     ('exoneration', 'Exonération de taxe'), ('avoir', 'Avoir'),
                                     ('normal', 'Normal')], 'Type', index=True, readonly=False)
    mode_paiement = fields.Selection([('cheque', 'Chèque'), ('espece', 'Espèce'), ('virement', 'Virement')],
                                     'Mode de paiement', index=True, readonly=False)
    taux_amount = fields.Float('Taux montant', compute=_computeSaleOrder, store=False, digits=(10, 2))

    @api.multi
    def _get_tax_amount_by_type(self, types):
        self.ensure_one()
        result = self._get_tax_amount_by_group()
        if types:
            for res in result:
                if res[0] == types:
                    return res[1]
        else:
            return 0


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    quantity = fields.Float(string='Quantity', digits=(10, 2), required=True, default=1)
    discount = fields.Float(string='Discount (%)', digits=(10, 2), default=0.0)
    price_unit = fields.Float(string='Unit Price', required=True, digits=(10, 0))
