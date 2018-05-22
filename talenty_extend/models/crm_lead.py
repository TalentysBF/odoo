# -*- coding:utf-8 -*-

from odoo import models, fields, api


class Lead(models.Model):
    _name = "crm.lead"
    _inherit = 'crm.lead'


    user_id = fields.Many2one('res.users', string='Commercial', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    a_vente = fields.Many2one('res.users', 'Avant Vente')
    referred = fields.Many2one('res.users', 'Apporté par')
