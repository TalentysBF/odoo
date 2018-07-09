# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import Number_To_Word
from odoo.exceptions import UserError
import math

_STATES = [
    ('draft', 'Brouillon'),
    ('paid', 'Payer'),
    ('avoir', 'Avoir')
]

class ZetaTransFacture(models.Model):
    _name = 'zeta.trans.facture'

    @api.model
    def decimales(self, f):
        if math.fabs(f - 0.0) > 1e-5:
             return f - math.floor(f)

    @api.multi
    def copy(self, default=None):
        if (not self.avoir) and (self.state != 'avoir'):
            self.state = 'avoir'
            if default is None:
                default = {}
            default['avoir'] = True
            default['facture_o'] = self.name
            default['state'] = 'avoir'
            default['n_a_p'] = -(self.n_a_p)
            default['n_a_p_bis'] = -(self.n_a_p)
            default['name'] = _('Avoir ') + self.name
            return super(ZetaTransFacture, self).copy(default)
        else:
            raise UserError(_('Cette Facture dispose deja d\'un avoir'))

    @api.multi
    def button_paid(self):
        self.get_paid()
        for rec in self:
            rec.state = 'paid'
        return True

    @api.multi
    def actualiser(self):
            self.fill_back()

    @api.model
    def create(self, vals):
        if (vals.get('name') == 'nouveau') and vals.get('code_facture'):
            vals['name'] = vals.get('code_facture') + '-' + self.env['ir.sequence'].next_by_code('zeta.trans.facture')
        client_id = vals.get('client_id')
        to_pay = vals.get('n_a_p_bis') + 10
        self.env.cr.execute("UPDATE res_partner SET to_pay=((SELECT to_pay FROM res_partner WHERE id=%s) + %s) WHERE id=%s", (client_id ,to_pay, client_id))
        self.env.cr.commit()
        return super(ZetaTransFacture, self).create(vals)

    @api.onchange('str_proforma')
    def fill_back(self):
        if self.str_proforma:
            for proforma in self.str_proforma:
                qte = proforma.qte
                colis = proforma.colis
                poids_net = proforma.poids_net
                poids_brut = proforma.poids_brut
                valeur_caf = proforma.valeur_caf
                valeur_mercurial = proforma.valeur_mercurial
                d_t_d = proforma.d_t_d
                transport = proforma.transport
                designation = proforma.designation
                t_s_ecor = proforma.t_s_ecor
                t_v_a = proforma.t_v_a
                vaccation = proforma.vaccation
                b_i_c = proforma.b_i_c
                assurance = proforma.assurance
                p_m_d = proforma.p_m_d
                camionage = proforma.camionage
                rem_doc = proforma.rem_doc
                rem_doc_nom = proforma.rem_doc_nom
                d_d_u = proforma.d_d_u
                decl_douane = proforma.str_minute.decl_douane
                facture = proforma.facture
                facture_mnt = proforma.facture_mnt
                stationement = proforma.stationement
                t_v_a_d_1 = proforma.t_v_a_d_1
                t_v_a_d_2 = proforma.t_v_a_d_2
                d_f_g = proforma.d_f_g
                total_debours = proforma.total_debours
                ouverture = proforma.ouverture
                imprime = proforma.imprime
                h_a_d = proforma.h_a_d
                divers_debours = proforma.divers_debours
                divers_inter = proforma.divers_inter
                total_int = proforma.total_int
                commission_a = proforma.commission_a
                commission_t = proforma.commission_t
                commission_d = proforma.commission_d
                t_v_a_int = proforma.t_v_a_int
                total_ttc = proforma.total_ttc
                note = proforma.note
                forme_j = proforma.forme_j
                regime_i = proforma.regime_i
                domiciliation_f = proforma.domiciliation_f
                address_cadastrale = proforma.address_cadastrale
                fax = proforma.fax

            self.update({
                'designation': designation,
                'qte': qte,
                'poids_net': poids_net,
                'poids_brut': poids_brut,
                'valeur_caf': valeur_caf,
                'valeur_mercurial': valeur_mercurial,
                'transport': transport,
                'd_t_d': d_t_d,
                't_s_ecor': t_s_ecor,
                'vaccation': vaccation,
                'assurance': assurance,
                'p_m_d': p_m_d,
                't_v_a_d_1': t_v_a_d_1,
                't_v_a_d_2': t_v_a_d_2,
                'camionage': camionage,
                'rem_doc': rem_doc,
                'rem_doc_nom': rem_doc_nom,
                'd_d_u': d_d_u,
                'facture': facture,
                'facture_mnt': facture_mnt,
                'stationement': stationement,
                'd_f_g': d_f_g,
                'total_debours': total_debours,
                'ouverture': ouverture,
                'imprime': imprime,
                'h_a_d': h_a_d,
                'real_had': h_a_d,
                'divers_debours': divers_debours,
                'divers_inter': divers_inter,
                'total_int': total_int,
                'commission_a': commission_a,
                'commission_t': commission_t,
                'commission_d': commission_d,
                't_v_a_int': t_v_a_int,
                'colis': colis,
                'total_ttc': total_ttc,
                't_v_a': t_v_a,
                'decl_douane': decl_douane,
                'b_i_c': b_i_c,
                'note': note,
                'forme_j': forme_j,
                'regime_i': regime_i,
                'domiciliation_f': domiciliation_f,
                'address_cadastrale': address_cadastrale,
                'fax': fax
            })

    @api.onchange('total_int', 't_v_a_int_value')
    def onchange_compute_total_tva(self):
        self.t_v_a_int = round((float(self.total_int) * self.t_v_a_int_value) / 100)

    @api.depends('total_int', 't_v_a_int')
    def _compute_ttc(self):
        self.total_ttc = self.total_int + self.t_v_a_int

    @api.onchange('total_ttc')
    def onchange_total_ttc(self):
        self.total_ttc_bis = self.total_ttc

    @api.depends('t_a_f', 'total_debours', 'total_ttc', 'n_a_p_bis')
    def _compute_nap(self):
        self.n_a_p = self.t_a_f + self.total_debours + self.total_ttc
        if self.n_a_p_bis == - self.n_a_p:
            self.n_a_p = self.n_a_p_bis

    @api.onchange('n_a_p')
    def onchange_nap(self):
        self.n_a_p_bis = self.n_a_p

    @api.onchange('str_proforma')
    def onchange_compute_dossier(self):
        client = self.str_proforma
        self.res_client = client.res_client
        self.numero_dossier = client.numero_dossier
        self.code_client = client.code_client
        self.type_operation = client.str_minute.str_dossier.type_operation
        self.code_facture = client.str_minute.str_dossier.str_bureau.code_facture
        self.nom_client = client.nom_client
        self.rccm = client.rccm
        self.boite_postal = client.boite_postal
        self.ifu = client.ifu
        self.telephone = client.telephone
        self.ref_p_f = client.ref_p_f
        self.ref_f_f = client.ref_f_f

    @api.onchange('res_client')
    def onchange_res_client(self):
        client = self.res_client
        self.code_client = client.numero_client
        self.nom_client = client.name
        self.rccm = client.rccm
        self.boite_postal = client.boite_postale
        self.ifu = client.ifu
        self.telephone = client.phone
        self.forme_j = client.forme_j
        self.regime_i = client.regime_i
        self.domiciliation_f = client.domiciliation_f
        self.address_cadastrale = client.address_cadastrale
        self.fax = client.fax
	self.client_id = client.id

    @api.depends('d_t_d')
    def _compute_taf(self):
        self.t_a_f = self.d_t_d

    @api.onchange('str_proforma')
    def onchange_things(self):
        self.to_pay = self.str_proforma.str_minute.res_client.to_pay
        self.client_id = self.str_proforma.str_minute.res_client.id

    test = fields.Char('Test')

    value = fields.Char('Valeur', compute='_compute_code')

    name = fields.Char(default='nouveau', required=True, string='Facture', readonly=False, index=True, copy=False)

    facture_o = fields.Char('Facture Origine')

    res_client = fields.Many2one('res.partner', 'Client direct')
    str_minute = fields.Many2one('zeta.trans.minute', 'Minute')
    str_proforma = fields.Many2one('zeta.trans.proforma', 'Proforma')
    code_facture = fields.Char('Code Facture')
    str_bureau = fields.Many2one('zeta.trans.bureau', 'Bureau')
    avoir = fields.Boolean(default=False)
    amende = fields.Integer('Amende douane')
    decl_douane = fields.Selection(
        [('decl', 'Decl De Douane Unique'), ('laboratoire', 'Laboratoire'), ('phyto', 'Phyto'),
         ('certif', 'Certif.Vete'), ('autres', 'Autres')], 'Nom DDU')
    @api.depends('str_bureau')
    def _compute_code(self):
        self.value = self.str_bureau.code_journal

    @api.onchange('value')
    def onchange_value(self):
        self.code_journal = self.str_bureau.code_journal
        self.compte_analytique = self.str_bureau.compte_analytique

    # INFO CLIENT
    forme_j = fields.Char()
    regime_i = fields.Char()
    domiciliation_f = fields.Char()
    nom_client = fields.Char()
    boite_postal = fields.Char()
    address_cadastrale = fields.Char()
    rccm = fields.Char()
    ifu = fields.Char()
    telephone = fields.Char()
    fax = fields.Char()
    code_journal = fields.Char('Code Journal')
    compte_analytique = fields.Char('Compte Analytique')

    # HEAD
    designation = fields.Text('Désignation')
    date_create = fields.Date('Date Création', required=True)
    qte = fields.Integer('Quantité')
    colis = fields.Integer('Colis')
    poids_brut = fields.Integer('Poids Brut')
    poids_net = fields.Integer('Poids Net')
    valeur_caf = fields.Float('Valeur Caf', digits=(32, 0))
    valeur_mercurial = fields.Integer('Valeur Mercuriale')
    transport = fields.Text('Mode de Transport')

    # AVANCE DE FONDS
    d_t_d = fields.Integer('Droits et Taxes Douane')
    t_v_a = fields.Integer('Dont TVA')
    b_i_c = fields.Integer('Dont BIC')
    t_a_f = fields.Integer('Total Avances de Fonds', compute='_compute_taf')

    @api.depends('t_s_ecor', 'vaccation', 'assurance', 'p_m_d', 't_v_a_d_1', 'camionage', 'rem_doc',
                 'd_d_u', 'stationement', 't_v_a_d_2', 'd_f_g', 'divers_debours', 'facture_mnt')
    def _compute_total_debours(self):
            self.total_debours = self.t_s_ecor + self.vaccation + self.assurance + self.p_m_d + self.t_v_a_d_1 \
                              + \
                              self.camionage + self.rem_doc + self.d_d_u + self.stationement + self.t_v_a_d_2\
                              + \
                              self.d_f_g + self.divers_debours + self.facture_mnt

    @api.onchange('p_m_d')
    def onchanche_compute_tva_1(self):
        value = (float(self.p_m_d) * 18) / 100
        if self.decimales(value) >= 0.5:
            self.t_v_a_d_1 = math.ceil(value)
        else:
            self.t_v_a_d_1 = round(value)

    @api.onchange('stationement')
    def onchange_compute_tva_2(self):
        value = (float(self.stationement) * 18) / 100
        if self.decimales(value) >= 0.05:
            self.t_v_a_d_2 = math.ceil(value)
        else:
            self.t_v_a_d_2 = round(value)

    # DEBOURS
    t_s_ecor = fields.Integer('T.S ECOR')
    vaccation = fields.Integer('Vacation Douanes')
    assurance = fields.Integer('Assurance Douanes')
    bool_assurance = fields.Boolean('Inclure Assurance', default=True)
    p_m_d = fields.Integer('Passage Mag/Douane')
    t_v_a_d_1 = fields.Integer('TVA', readonly=False)
    camionage = fields.Integer('Camionnage Manutention')
    rem_doc = fields.Integer('Remise Doc')
    rem_doc_nom = fields.Char('Nom Remise Doc')
    d_d_u = fields.Integer('DDU')
    facture = fields.Char('Facture Frontière')
    frontiere = fields.Selection(
        [('C0003', 'Niangologo'), ('C0004', 'Sinkence'), ('C0006', 'Dakola'),
         ('C0007', 'Nadiagou'), ('C0008', 'Fada'), ('C0009','Ouessa'), ('C0010','Faramana'), ('C0011','Koloko'), ('0', 'Autres')],
         'Frontiere', required=True)
    facture_mnt = fields.Integer('Montant Facture Frontière')
    stationement = fields.Integer('Stationnement')
    t_v_a_d_2 = fields.Integer('TVA', readonly=False)
    d_f_g = fields.Integer('Douane Fonds de Garantie')
    divers_debours = fields.Integer('Divers')
    total_debours = fields.Integer('TOTAL Débours', compute='_compute_total_debours')

    @api.depends('ouverture', 'imprime', 'h_a_d', 'commission_a', 'commission_d', 'commission_t', 'divers_inter')
    def _compute_total_int(self):
        self.total_int = self.ouverture + self.imprime + self.h_a_d + self.commission_a + self.commission_d \
                         + \
                         self.commission_t + self.divers_inter

    @api.onchange('total_int')
    def onchange_total_int(self):
        self.total_int_bis = self.total_int

    # INTERVANTIONS
    ouverture = fields.Integer('Ouverture de Dossier')
    imprime = fields.Integer('Imprimés et Timbres')
    h_a_d = fields.Integer('HAD')
    real_had = fields.Integer('HAD')
    commission_a = fields.Integer('Commission/Avances de Fonds')
    commission_t = fields.Integer('Commission de transit')
    commission_d = fields.Integer('Commision/Débours')
    divers_inter = fields.Integer('Divers')
    total_int = fields.Integer('Total Interventions HT', compute='_compute_total_int')
    total_int_bis = fields.Integer('Total Interventions HT')
    t_v_a_int = fields.Integer(string='TVA sur interventions', readonly=False)
    t_v_a_int_value = fields.Integer(string='TVA sur interventions %', default=18)
    total_ttc = fields.Integer(string='Total Interventions TTC', compute='_compute_ttc')
    total_ttc_bis = fields.Integer(string='Total Interventions TTC')
    numero_dossier = fields.Char('Numéro de dossier')
    code_client = fields.Char('Code Client')
    type_operation = fields.Char('Type d\'opération')
    note = fields.Text('Commentaires')

    # REMISE HAD
    remise_had = fields.Float('Remise HAD')

    to_pay = fields.Integer()
    client_id = fields.Integer()

    # REFERENCE FOURNISSEUR
    ref_p_f = fields.Char('Référence Proforma Fournisseur')
    ref_f_f = fields.Char('Référence Facture Fournisseur')

    # CONDITION VENTE
    condition_vente = fields.Boolean('Afficher conditions de règlement', default=True)

    # NET A PAYER
    n_a_p = fields.Integer(string='NET A PAYER', compute='_compute_nap')
    n_a_p_bis = fields.Integer(string='NET A PAYER')

    @api.depends('n_a_p')
    def get_amount_letter(self):
        n_a_p = - self.n_a_p if self.n_a_p < 0 else self.n_a_p
        if n_a_p > 0:
            amount_letter = Number_To_Word.Number_To_Word(n_a_p, 'fr', 'FRANCS CFA', '')
            self.amount_total_letter = amount_letter


    @api.model
    def get_paid(self):
	if self.str_proforma:
		client = self.str_proforma.str_minute.res_client
	else:
		client = self.res_client
	to_pay = client.to_pay
        paid = client.paid
        to_pay = to_pay - self.n_a_p
        paid = paid + self.n_a_p
        self.env.cr.execute("UPDATE res_partner SET to_pay=%s, paid=%s WHERE id=%s", (to_pay, paid, client.id))
        self.env.cr.commit()

    amount_total_letter = fields.Char('Montant total en lettre', required=False, compute='get_amount_letter')

    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')
