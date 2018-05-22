# -*- coding:utf-8 -*-

from odoo import api, fields, models


class TalentysCaisse(models.Model):
    _inherit = "talentys.caisse"

    responsable = fields.Many2one('res.users', 'Responsable Caisse')
    ouverture = fields.Integer('Solde a l\'ouverture')
    fermeture = fields.Integer('Solde de cloture')
    lines_id = fields.One2many('talentys.caisse.line', 'caisse_id', 'Transactions')


class TalentysCaisseLine(models.Model):
    _inherit = "talentys.caisse.line"

    caisse = fields.Many2one('talentys.caisse', 'Caisse')

    motif = fields.Char('Libelle', required=True)
    genre = fields.Selection([('input', 'Entree'), ('output', 'sortie')], 'Type d\'operation', required=True)
    montant = fields.Integer('Montant transaction', required=True)
