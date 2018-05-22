# -*- coding: utf-8 -*-

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rccm = fields.Char('RCCM')
    ifu = fields.Char('IFU')
    r_i = fields.Char('Regime d\'imposition')
    d_f = fields.Char('Division Fiscale')
    adresse_cadastrale = fields.Char('Adresse Cadastrale')
