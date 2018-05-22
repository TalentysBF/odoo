# -*- coding: utf-8 -*-

from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    rccm = fields.Char('RCCM')
    ifu = fields.Char('IFU')
    r_i = fields.Char('Regime d\'imposition')
    d_f = fields.Char('Division fiscale')
