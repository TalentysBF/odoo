# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ZetaTransDossier(models.Model):
    _name = 'zeta.trans.dossier'

    @api.depends('str_bureau')
    def _compute_code_dossier(self):
        for dossier in self:
            dossier.code_dossier = dossier.str_bureau.code_dossier

    @api.onchange('str_bureau')
    def onchange_bureau(self):
        self.pre_name = self.str_bureau.code_dossier

    @api.model
    def create(self, vals):
        if (vals.get('name') == 'nouveau') and vals.get('pre_name'):
            vals['name'] = vals.get('pre_name') + '.' + self.env['ir.sequence'].next_by_code('zeta.trans.dossier')
        return super(ZetaTransDossier, self).create(vals)

    name = fields.Char(default='nouveau', required=True, string='Dossier/Transit', index=True, copy=False,
                       readonly=False)
    pre_name = fields.Char()
    test = fields.Char('Test')
    type_operation = fields.Selection([('export', 'Exportation'), ('import', 'Importation')], 'Type d\'opération')
    client = fields.Many2one('res.partner', 'Client')
    str_bureau = fields.Many2one('zeta.trans.bureau', 'Bureau')
    code_dossier = fields.Char('Code Dossier', compute='_compute_code_dossier')
    date = fields.Datetime('Date')

    # MARCHANDISE
    nbr_nature = fields.Char('Nombre et Nature des Colis')
    designation = fields.Char('Designation')
    destinataire = fields.Many2one('res.partner', 'Destinataire')
    poids_brut = fields.Integer('Poids Brut (KG)')
    expediteur = fields.Many2one('res.partner', 'Expéditeur')
    poids_net = fields.Integer('Poids Net (KG)')
    transport = fields.Selection(
        [('maritime', 'Maritime'), ('ferovier', 'Ferroviaire'), ('terrestre', 'Terrestre'), ('aerien', 'Aérien')],
        'Moyen de transport')
    maritime = fields.Boolean('Maritime')
    ferovier = fields.Boolean('Ferroviaire')
    terrestre = fields.Boolean('Terrestre')
    aerien = fields.Boolean('Aérien')
    n_repertoire = fields.Char('N°. de Répertoire')
    n_declaration = fields.Char('N°. de Déclaration')
    n_liquidation = fields.Char('N°. de Liquidation')
    n_rangement = fields.Char('N°. Boite de Rangement')
    n_transport = fields.Char('N°. Moyen de Transport')
    n_bl = fields.Char('N°. Du BL')
    n_conteneur = fields.Char('N°. Du Conteneur')
    n_sommier = fields.Char('N°. De Sommier')
    p_j_1 = fields.Binary('Pièce Justificative 1')
    p_j_2 = fields.Binary('Pièce Justificative 2')
    observation = fields.Text('Observations')
    ref_p_f = fields.Char('Référence Proforma Fournisseur')
    ref_f_f = fields.Char('Référence Facture Fournisseur')
