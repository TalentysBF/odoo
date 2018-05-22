# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import Number_To_Word
import math


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        result = {'domain': domain}
        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result
        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name
        self._compute_tax_id()
        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['prix_gpl_real'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        return result

    @api.onchange('prix_gpl', 'remise_fournisseur', 'marge', 'frais_approche', 'product_uom_qty', 'prix_gpl_real', 'prix_gpl_value')
    def _get_price_unit(self):
        self.prix_gpl = self.prix_gpl_real * self.prix_gpl_value
        value = self.prix_gpl
        remise_fournisseur = value - (value * (self.remise_fournisseur / 100))
        self.remise_fournisseur_value = math.ceil(value * (self.remise_fournisseur / 100))
        frais_approche = remise_fournisseur + math.ceil(remise_fournisseur * (self.frais_approche / 100))
        self.frais_approche_value = math.ceil(remise_fournisseur * (self.frais_approche / 100))
        self.purchase_price = frais_approche
        marge = math.ceil(frais_approche / (1 - (self.marge / 100)))
        self.marge_value = marge - frais_approche
        self.price_unit = marge

    @api.onchange('devise')
    def onchange_devise(self):
        if self.devise == 'euro':
            self.prix_gpl_value = 656
        elif self.devise == 'dolar':
            self.prix_gpl_value = 556
        elif self.devise == 'aed':
            self.prix_gpl_value = 147

    prix_gpl_real = fields.Float(string='Prix Public en devise', required=False)
    devise = fields.Selection([('euro', 'EUR'), ('dolar', 'USD'), ('aed', 'AED')])
    prix_gpl_value = fields.Float(string='Prix GPL Value', required=False, default=1)

    prix_gpl = fields.Integer(string='Prix Public (XOF)', required=False)
    remise_fournisseur = fields.Float(
        string="Remise Fr (%)", required=False, default=0.0)
    remise_fournisseur_value = fields.Integer('Remise Fournisseur Value')
    marge = fields.Float(string="Marge (%)", required=False, default=0.0)
    marge_value = fields.Integer('Marge Value')
    frais_approche = fields.Float(
        string="Frais d'approche Coef", required=False, default=0.0)
    frais_approche_value = fields.Integer('Frais Approche Value')
    product_uom_qty = fields.Float(string='Quantity', digits=(12, 2), required=True, default=1.0)
    result = fields.Float()

    first_msg = fields.Html(
        'Pricelist PDF',
        default="""
        <embed src="http://micromut.fr/internet/Pdf/Mieux_utiliser_Google.pdf" type="application/pdf"   height="300px" width="100%">
        """, sanitize=False)

    state = fields.Selection([
        ('draft', 'BOQ'),
        ('validate', 'A Valider'),
        ('waiting', 'En Attente'),
        ('auto', 'A Autorisés'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('archive', 'Archive'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

#    @api.multi
#    def action_google(self):
#        self.ensure_one()
#        return {
#            'type': 'ir.actions.act_url',
#            'url': 'http://www.google.com',
#            'target': 'new',
#        }

    @api.multi
    def print_quotation(self):
        self.write({'state': 'sent'})
        return self.env.ref('sale.action_report_saleorder').report_action(self)

    @api.multi
    def action_archive(self):
        self.last_state = self.state
        self.write({'state': 'archive'})

    @api.multi
    def action_unarchive(self):
        self.state = self.last_state

    @api.multi
    def action_validate(self):
        self.write({'state': 'validate'})

    @api.multi
    def action_auto(self):
        self.write({'state': 'auto'})

    @api.multi
    def action_waiting(self):
        self.write({'state': 'waiting'})

    @api.depends('amount_total')
    def get_amount_letter(self):
        if self.amount_total:
            amount_letter = Number_To_Word.Number_To_Word(self.amount_total, 'fr', 'Francs CFA', '')
            self.amount_total_letter = amount_letter

    @api.multi
    def action_rejected(self):
        self.write({'state': 'rejected'})

    amount_total_letter = fields.Char('Montant total en lettre', required=False, compute='get_amount_letter')

    last_state = fields.Char('Last state')
    commercial = fields.Many2one('res.users', 'Commercial')
    avant_vente = fields.Many2one('res.users', 'Avant vente')
    apporteur = fields.Many2one('res.users', 'Apporteur d\'affaire')

    fret = fields.Integer('Valeur Fret')
    c_d_f = fields.Many2one('res.partner', 'Charges de fonctionnement')
    douane = fields.Many2one('res.partner', 'Douane')

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

    state = fields.Selection([
        ('draft', 'BOQ'),
        ('validate', 'A Saisir'),
        ('auto', 'Saisi'),
        ('waiting', 'En Attente'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('archive', 'Archive'),
        ('done', 'Locked'),
        ('rejected', 'Rejeter'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')