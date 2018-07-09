# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ZetaTransTransaction(models.Model):
    _name = 'zeta.trans.transaction'

    @api.depends('entree', 'sortie')
    def _conpute_monsolde(self):
        self.solde = self.entree - self.sortie

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('zeta.trans.transaction')
        return super(ZetaTransTransaction, self).create(vals)

    date = fields.Datetime(string='Date')
    name = fields.Char(default='nouveau', required=True, string='Transaction', readonly=True)
    libelle = fields.Char('Libellé')
    benefic = fields.Char('Benéficiaire')
    #z_caisse = fields.Many2one('zeta.trans.caisse', 'Caisse', default=1)
    montant = fields.Integer(string='Montant')
    type_transaction = fields.Selection([('entree', 'Entree'), ('sortie', 'Sortie')], 'Type Transation')
    name_dossier = fields.Many2one('zeta.trans.dossier', string='Dossier')
    caissier = fields.Char('La Caissière')
    controleur = fields.Char('Le Contrôleur')
