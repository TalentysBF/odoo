# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ZetaTransArticle(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    is_zeta_trans_article = fields.Boolean('Zeta Transit acticle')