# -*- coding: utf-8 -*-

from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    header_logo = fields.Binary('Entête de rapport', required=False)
    footer_logo = fields.Binary('Pied de page rapport', required=False)
