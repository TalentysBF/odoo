# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import had


class ZetaTransHad(models.Model):
    _name = 'zeta.trans.had'
    _inherit = 'res.config.settings'

    @api.onchange('secteur', 'valeur_caf')
    def onchange_had(self):
        self.honoraire = had.compute_had(int(self.secteur), self.valeur_caf)

    valeur_caf = fields.Integer('Valeur CAF')
    honoraire = fields.Integer('H.A.D', readonly=False)
    secteur = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], string='Section')
