# -*- coding:utf-8 -*-

from odoo import api, fields, models

_STATES = [
    ('draft', 'Brouillon'),
    ('ouvert', 'Ouvert'),
    ('fermer', 'Fermer')
]

class TalentysCaisse(models.Model):
    _name = "talentys.caisse"

    @api.multi
    def button_open(self):
        self.fermeture = self.ouverture
        self.d_ouverture = fields.Datetime.now()
        for rec in self:
            rec.state = 'ouvert'
        return True

    @api.multi
    def button_fermer(self):
        self.d_fermeture = fields.Datetime.now()
        for rec in self:
            rec.state = 'fermer'
        return True

    @api.onchange('lines_id')
    def onchange_amount_all(self):
        for trans in self:
            value = 0
            for line in trans.lines_id:
                if line.genre == 'input':
                    value += line.montant
                elif line.genre == 'output':
                    value -= line.montant
            trans.fermeture = trans.ouverture + value

    name = fields.Char('Caisse', default="Caisse Exemple")
    responsable = fields.Many2one('res.users', 'Responsable Caisse')
    ouverture = fields.Integer('Solde a l\'ouverture')
    d_ouverture = fields.Datetime('Date Ouverture')
    str_bureau = fields.Many2one('zeta.trans.bureau', 'Bureau', required=True)
    fermeture = fields.Integer('Solde de cloture')
    d_fermeture = fields.Datetime('Date Fermeture')
    lines_id = fields.One2many('talentys.caisse.line', 'caisse_id', 'Transactions')

    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')

class TalentysCaisseLine(models.Model):
    _name = "talentys.caisse.line"

    @api.model
    def create(self, vals):
        vals['d_transaction'] = fields.Datetime.now()
        vals['name'] = self.env['ir.sequence'].next_by_code('talentys_caisse') or '/'
        return super(TalentysCaisseLine, self).create(vals)

    name = fields.Char('Libelle', required=True, default='Ligne')
    d_transaction = fields.Datetime('Date Transaction')
    caisse_id = fields.Many2one('talentys.caisse', 'Caisse')
    motif = fields.Text('Motif', required=True)
    genre = fields.Selection([('input', 'Entree'), ('output', 'Sortie')], 'Type d\'operation', required=True)
    montant = fields.Integer('Montant transaction', required=True)
