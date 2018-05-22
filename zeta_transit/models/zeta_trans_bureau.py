# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ZetaTransBureau(models.Model):
    _name = 'zeta.trans.bureau'

    name = fields.Char('Nom Bureau')
    code_dossier = fields.Char('Code Dossier')
    code_facture = fields.Char('Code Facture')
    code_proforma = fields.Char('Code Proforma')
