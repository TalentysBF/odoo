# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ZetaTransClient(models.Model):
    _inherit = 'res.partner'

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            partner.company_type = partner.company_type

    @api.onchange('company_type')
    def onchange_company_type(self):
        self._compute_company_type

    test = fields.Char('Terre')

    company_type = fields.Selection(string='Company Type',
                                    selection=[('persone', 'Individuelle'), ('compagnie', 'SARL'), ('sa', 'SA')],
                                    default='sa',
                                    readonly=False)

    street = fields.Char(string="Adresse Geographique", translate=False)
    street2 = fields.Char(string="Adresse Cadastrale", translate=False)
    boite_postale = fields.Char('Boite Postale')
    address_cadastrale = fields.Char('Adresse Cadastrale')
    rccm = fields.Char(string='RCCM')
    ifu = fields.Char(string='IFU')
    numero_client = fields.Char(string="Numero Client", default='41110000', required=True)
    city = fields.Char(string='Ville')
    country_id = fields.Many2one('res.country', string="Pays", ondelete='restrict')
    is_zeta_trans_destinatair = fields.Boolean('Destinataire')
    is_zeta_trans_expediteur = fields.Boolean('Expediteur')
    is_zeta_trans_client = fields.Boolean('Client')
    forme_j = fields.Char('Forme Juridique')
    regime_i = fields.Char('Régime D\'imposition')
    domiciliation_f = fields.Char('Domiciliation Fiscale')
    fax = fields.Char('Fax')

    # SOLDE
    to_pay = fields.Integer('Debit')
    paid = fields.Integer('Credit')
