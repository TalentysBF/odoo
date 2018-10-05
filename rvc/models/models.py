# -*- coding: utf-8 -*-

from odoo import models, fields


class talentys_rvc(models.Model):
    _name = 'talentys.rvc'
    _description = 'talentys RVC'

    ####
    #### Informations client et commercial
    ####
    name = fields.Many2one('res.users', 'Commercial', required=True, default=lambda self: self.env.user)
    client = fields.Many2one('res.partner', 'Client', required=True)
    datej = fields.Date('Date', required=True)
    lieu = fields.Text('Lieu', required=True)
    participant = fields.One2many('talentys.rvc.participant', 'rvc', 'Participant', copy=True)

    ###
    ### Informations COMPTE RENDU
    ###

    cr = fields.Text('Compte Rendu', required=True)

    ###
    ### Informations Actions à mener
    ###

    action = fields.Text('Actions', required=True)

    ###many2many_tags allows us to select only res.users name in selected fields
    ###acteur=fields.Many2many('res.users', "many2many_tags",string="Acteurs")

    #######################################################################################################
    ###many2many_checkboxes allows us to select many options with checkboxes options
    ###acteur=fields.Many2many('res.users', "many2many_checkboxes",string="Acteurs")
    acteur = fields.Many2many('res.users', "many2many_tags", string="Acteurs")
    deadline = fields.Date('Deadline')

    class talentys_rvc_participant(models.Model):
        _name = 'talentys.rvc.participant'
        _description = 'Talentys rvc participant'

        rvc = fields.Many2one('talentys.rvc')
        name = fields.Many2one('res.users', 'Participant', required=True)
        poste = fields.Char('Poste')
        tel = fields.Char('Téléphone')
        mail = fields.Char('Mail')

    class calendar_event(models.Model):
        _name = 'calendar.event'
        _inherit = 'calendar.event'
        _description = 'talentys RVC'

        rvc_calendar = fields.Many2one('talentys.rvc', 'Rapport de Visite')
