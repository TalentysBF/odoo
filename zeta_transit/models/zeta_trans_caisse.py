# -*- coding: utf-8 -*-

from odoo import api, fields, models

_STATES = [
    ('ouvert', 'Ouvert'),
    ('ferme', 'Fermé'),
    ('attente', 'En attente')
]


class ZetaTransCaisse(models.Model):
    _name = 'zeta.trans.caisse'
    _inherit = 'res.config.settings'

    @api.depends('entree', 'sortie')
    def _conpute_monsolde(self):
        self.solde = self.entree - self.sortie

    test = fields.Char('Test', default='Terre')

    name = fields.Char(default='nouveau', readonly=True, required=True, string='Caisse')
    date = fields.Datetime('Date')
    solde = fields.Integer('Solde')
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='attente')

    # res_transaction_id = fields.One2many('zeta.trans.transaction', 'z_caisse', 'Transactions', copy=True, store=True)


class ZetaTransCaisseKanban(models.Model):
    _name = 'zeta.trans.caisse.kanban'

    @api.model
    def create(self, vals):
        if vals.get('type_mouvement') == 'recette':
            solde = vals.get('solde') + vals.get('montant')
        else:
            solde = vals.get('solde') - vals.get('montant')
        self.env.cr.execute("UPDATE zeta_trans_caisse_solde_kanban SET solde=%s", (solde,))
        self.env.cr.commit()
        return super(ZetaTransCaisseKanban, self).create(vals)

    @api.multi
    def test_test(self):
        return True

    @api.model
    def _get_numero_caisse_kanban(self):
        try:
            self.env.cr.execute("SELECT name FROM zeta_trans_caisse WHERE id = (SELECT MAX(id) FROM zeta_trans_caisse)")
            value = self.env.cr.fetchone()[0]
        except:
            value = "0"
        return value

    test = fields.Char('Test', default='Terre')

    name = fields.Char(string='Transaction')
    date = fields.Datetime('Date')
    autheur = fields.Many2one('res.users', default=lambda self: self.env.user)
    solde_link = fields.Many2one('zeta.trans.caisse.solde.kanban', 'Solde', default=1)
    solde = fields.Integer('Solde', default=lambda self: self.solde_link.solde)
    beneficiaire = fields.Many2one('res.users', 'Beneficiare')
    n_dossier = fields.Many2one('zeta.trans.dossier', 'Dossier')
    operation = fields.Char('Libellé de l\'opération')
    montant = fields.Integer('Montant')
    type_mouvement = fields.Selection([('recette', 'Récettes'), ('depense', 'Dépenses')], required=True)
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='attente')


class ZetaTransCaisseSoldeKanban(models.Model):
    _name = 'zeta.trans.caisse.solde.kanban'

    solde = fields.Integer('Solde Caisse')
