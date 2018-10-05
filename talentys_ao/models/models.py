# -*- coding: utf-8 -*-

from odoo import api, models, fields

class talentys_ao(models.Model):
    _name = 'talentys.ao'
    _description = 'talentys AO'

    @api.one
    def consult(self):
        self.state = 'consulted'

    @api.one
    def spread(self):
        self.state = 'spread'

    @api.one
    def validate(self):
        self.state = 'validated'

    @api.one
    def validate_a(self):
        self.state = 'validated_a'

    @api.one
    def validate_t(self):
        self.state = 'validated_t'

    @api.one
    def validate_f(self):
        self.state = 'validated_f'

    @api.one
    def reject(self):
        self.state = 'reject'

    @api.onchange('lot')
    def onchange_lot(self):
        if self.state in ['draft','consulted']:
            self.price = 0
            for lots in self:
                for item in lots.lot:
                    self.price += item.prix

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('talentys.ao') or '/'
        return super(talentys_ao, self).create(vals)

    ####
    #### Informations about Call for tender
    ####

    state = fields.Selection([('draft', 'Brouillon'), ('consulted', 'AO Consulter'), ('spread', 'Diffuser'),
                              ('validated', 'Validation General'), ('validated_a', 'Validation Adm'),
                              ('validated_t', 'Validation Tech'), ('validated_f', 'En attente de depot'),
                              ('done', 'Deposer'), ('reject', 'Rejeter')], default='draft')
    name = fields.Char(default='nouveau', required=True, string='Numéro AO', readonly=True, index=True, copy=False)
    nom = fields.Char('Nom AO', required=True)
    client = fields.Many2one('res.partner', 'Client', required=True)
    datec = fields.Date('Date consultation', required=True, default= fields.DateTime.Now())
    dated = fields.Date('Date d\'échance', required=True)
    comment = fields.Text('Commentaire')
    ao_file = fields.Binary('Fichier AO')
    price = fields.Integer('Prix AO')
    cr=fields.Binary("Compte Rendu")
    lot = fields.One2many('talentys.ao.lot', 'ao', 'Lots', copy=True)


class talentys_ao_lot(models.Model):
    _name = 'talentys.ao.lot'
    _description = 'Talentys ao lot'

    @api.onchange('val_admin','val_tech')
    def valideFinal(self):
        if self.val_admin and self.val_tech:
            self.val_final = True


    ao = fields.Many2one('talentys.ao')
    name = fields.Char('Libellé lot')
    descrip = fields.Char('Descriptif')
    amount = fields.Integer('Garantie de soumission')
    divers = fields.Text('Divers')
    prix = fields.Integer('Prix d\'achat lot');
    fichier = fields.Binary('Fichier Lot');
    val_admin = fields.Boolean('Admin')
    val_tech = fields.Boolean('Tech')
    val_final = fields.Boolean('Validé')
    id_materiel = fields.One2many('talentys.ao.lot.materiel', 'id_lot_materiel', 'Materiel')
    id_technique = fields.One2many('talentys.ao.lot.technique', 'id_lot_technique', 'Technique')
    id_admin = fields.One2many('talentys.ao.lot.admin', 'id_lot_admin', 'Admin')


class talentys_ao_lot_materiel(models.Model):
    _name = 'talentys.ao.lot.materiel'
    _description = 'Talentys ao lot materiel'

    ###
    ### Informations about material requirements
    ###
    id_lot_materiel = fields.Many2one('talentys.ao.lot')
    des_m = fields.Char('Description')
    nb = fields.Integer('Nombre')


class talentys_ao_lot_technique(models.Model):
    _name = 'talentys.ao.lot.technique'
    _description = 'Talentys ao lot technique'

    ###
    ### Informations about technical requirements
    ###
    id_lot_technique = fields.Many2one('talentys.ao.lot')
    pos = fields.Char('Position')
    qualif = fields.Char('Qualifications')
    expg = fields.Integer('Expérience Globale')
    exppos = fields.Integer('Expérience Position similaire')


class talentys_ao_lot_admin(models.Model):
    _name = 'talentys.ao.lot.admin'
    _description = 'Talentys ao lot admin'
    ###
    ### Informations about administrative requirements
    ###  des_adm =  descriptif administration ie les exgigences administratives
    id_lot_admin = fields.Many2one('talentys.ao.lot')
    des_adm = fields.Text('Description')
