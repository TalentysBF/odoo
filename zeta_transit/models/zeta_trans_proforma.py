# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import Number_To_Word
import math


class ZetaTransProforma(models.Model):
    _name = 'zeta.trans.proforma'

    @api.model
    def decimales(self, f):
        if math.fabs(f - 0.0) > 1e-5:
            return f - math.floor(f)

    @api.multi
    def actualiser(self):
        self.fill_back()
        self.onchange_minute()

    @api.model
    def create(self, vals):
        if (vals.get('name') == 'nouveau') and vals.get('code_proforma'):
            vals['name'] = vals.get('code_proforma') + '-' + self.env['ir.sequence'].next_by_code('zeta.trans.proforma')
        return super(ZetaTransProforma, self).create(vals)

    @api.onchange('str_minute')
    def onchange_code_proforma(self):
        self.code_proforma = self.str_minute.str_dossier.str_bureau.code_proforma

    @api.onchange('str_minute')
    def fill_back(self):
        if self.str_minute:
            for minute in self.str_minute:
                qte = 0
                colis = 0
                poids_net = 0
                poids_brut = 0
                valeur_caf = 0
                valeur_mercurial = 0
                d_t_d = 0
                transport = ""
                for article in minute.res_article_id:
                    qte += article.qte_complete
                    colis += article.nbr_colis
                    poids_brut += article.int_poids_brut
                    poids_net += article.int_poids_net
                    valeur_caf += article.valeur_caf
                    valeur_mercurial += article.valeur_mercurial
                    if article.facturer:
                        d_t_d += article.droits_taxes
                if minute.str_dossier.maritime:
                    transport += " Maritime - "
                if minute.str_dossier.terrestre:
                    transport += " Terrestre - "
                if minute.str_dossier.ferovier:
                    transport += " Ferroviaire - "
                if minute.str_dossier.aerien:
                    transport += "  Aérien - "
                designation = minute.str_dossier.designation
                ts_ecor = minute.t_s_ecor
                t_v_a = minute.int_final_tva
                vaccation = minute.vaccation
                b_i_c = minute.int_final_aib
                assurance = minute.assurance
                p_m_d = minute.p_m_d_val
                camionage = minute.camionage_value
                rem_doc = minute.m_r_d
                rem_doc_nom = minute.rem_doc
                d_d_u = minute.decl_value
                facture = minute.f_f_n
                facture_mnt = minute.m_f_f
                stationement = minute.stationement
                tva_d1 = minute.t_v_a_d_1
                tva_d2 = minute.t_v_a_d_2
                d_f_g = minute.douane_fg
                total_debours = minute.total_debours
                ouverture_d = minute.ouverture_d
                imprime = minute.imprime
                honoraire = minute.honoraire
                divers_debours = minute.divers_debours
                divers_inter = minute.divers_inter
                total_ht = minute.total_ht
                avance = minute.avance
                transit = minute.transit
                debours = minute.debours
                t_v_a_d_3 = minute.t_v_a_d_3
                total_ttc = minute.total_ttc
            self.update({
                'designation': designation,
                'qte': qte,
                'poids_net': poids_net,
                'poids_brut': poids_brut,
                'valeur_caf': valeur_caf,
                'valeur_mercurial': valeur_mercurial,
                'transport': transport,
                'd_t_d': d_t_d,
                't_s_ecor': ts_ecor,
                'vaccation': vaccation,
                'assurance': assurance,
                'p_m_d': p_m_d,
                't_v_a_d_1': tva_d1,
                't_v_a_d_2': tva_d2,
                'camionage': camionage,
                'rem_doc': rem_doc,
                'rem_doc_nom': rem_doc_nom,
                'd_d_u': d_d_u,
                'facture': facture,
                'facture_mnt': facture_mnt,
                'stationement': stationement,
                'd_f_g': d_f_g,
                'total_debours': total_debours,
                'ouverture': ouverture_d,
                'imprime': imprime,
                'h_a_d': honoraire,
                'real_had': honoraire,
                'divers_debours': divers_debours,
                'divers_inter': divers_inter,
                'total_int': total_ht,
                'commission_a': avance,
                'commission_t': transit,
                'commission_d': debours,
                't_v_a_int': t_v_a_d_3,
                'colis': colis,
                'total_ttc': total_ttc,
                't_v_a': t_v_a,
                'b_i_c': b_i_c,
            })

    @api.onchange('total_int')
    def onchange_compute_total_tva(self):
        self.t_v_a_int = round((float(self.total_int) * 18) / 100)

    @api.depends('total_int', 't_v_a_int')
    def _compute_ttc(self):
        self.total_ttc = self.total_int + self.t_v_a_int

    @api.depends('t_a_f', 'total_debours', 'total_ttc')
    def _compute_nap(self):
        self.n_a_p = self.t_a_f + self.total_debours + self.total_ttc

    @api.depends('str_minute')
    def _compute_dossier(self):
        self.numero_dossier = self.str_minute.str_dossier.name

    @api.depends('str_minute')
    def _compute_code_client(self):
        self.code_client = self.str_minute.str_dossier.client.numero_client

    @api.depends('str_minute')
    def _compute_operation(self):
        self.type_operation = self.str_minute.str_dossier.type_operation

    @api.onchange('str_minute')
    def onchange_minute(self):
        client = self.str_minute.res_client
        self.nom_client = client.name
        self.rccm = client.rccm
        self.boite_postal = client.boite_postale
        self.ifu = client.ifu
        self.telephone = client.phone
        self.fax = client.fax
        self.forme_j = client.forme_j
        self.regime_i = client.regime_i
        self.domiciliation_f = client.domiciliation_f
        self.address_cadastrale = client.address_cadastrale

    @api.depends('d_t_d')
    def _compute_taf(self):
        self.t_a_f = self.d_t_d

    @api.depends('t_s_ecor', 'vaccation', 'assurance', 'p_m_d', 't_v_a_d_1',
                 'camionage', 'rem_doc', 'd_d_u', 'stationement', 't_v_a_d_2',
                 'd_f_g', 'divers_debours', 'facture_mnt')
    def _compute_total_debours(self):
        self.total_debours = self.t_s_ecor + self.vaccation + self.assurance + self.p_m_d + self.t_v_a_d_1 \
                             + \
                             self.camionage + self.rem_doc + self.d_d_u + self.stationement + self.t_v_a_d_2 \
                             + \
                             self.d_f_g + self.divers_debours + self.facture_mnt

    @api.onchange('p_m_d')
    def onchange_compute_tva_1(self):
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

    @api.depends('ouverture', 'imprime', 'h_a_d', 'commission_a', 'commission_d', 'commission_t', 'divers_inter')
    def _compute_total_int(self):
        self.total_int = self.ouverture + self.imprime + self.h_a_d + self.commission_a + self.commission_d \
                         + \
                         self.commission_t + self.divers_inter

    @api.depends('str_minute')
    def _compute_ref_fournisseur(self):
        ref = self.str_minute.str_dossier
        self.ref_p_f = ref.ref_p_f
        self.ref_f_f = ref.ref_f_f

    @api.depends('n_a_p')
    def get_amount_letter(self):
        if self.n_a_p:
            amount_letter = Number_To_Word.Number_To_Word(self.n_a_p, 'fr', 'FRANCS CFA', '')
            self.amount_total_letter = amount_letter

    test = fields.Char('Test')

    name = fields.Char(default='nouveau', required=True, string='Proforma', readonly=False, index=True, copy=False)

    res_client = fields.Many2one('res.partner', 'Client direct')
    str_minute = fields.Many2one('zeta.trans.minute', 'Minute')
    code_proforma = fields.Char('Code Proforma')

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

    # HEAD
    designation = fields.Text('Désignation')
    create_date = fields.Date('Date Création')
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

    # DEBOURS
    t_s_ecor = fields.Integer('T.S.ECOR')
    vaccation = fields.Integer('Vaccation Douanes')
    assurance = fields.Integer('Assurance Douanes')
    bool_assurance = fields.Boolean('Inclure Assurance', default=True)
    p_m_d = fields.Integer('Passage Mag/Douane')
    t_v_a_d_1 = fields.Integer('TVA', readonly=False)
    camionage = fields.Integer('Camionnage Manutention')
    rem_doc = fields.Integer('Remise Doc')
    rem_doc_nom = fields.Char('Nom Remise Doc')
    d_d_u = fields.Integer('DDU')
    facture = fields.Char('Facture Frontière')
    facture_mnt = fields.Integer('Montant Facture Frontière')
    stationement = fields.Integer('Stationnement')
    t_v_a_d_2 = fields.Integer('TVA', readonly=False)
    d_f_g = fields.Integer('Douane Fonds de Garantie')
    divers_debours = fields.Integer('Divers')
    total_debours = fields.Integer('TOTAL Débours', compute='_compute_total_debours')

    # INTERVANTIONS
    ouverture = fields.Integer('Ouverture de Dossier')
    imprime = fields.Integer('Imprimés et Timbres')
    h_a_d = fields.Integer('HAD')
    real_had = fields.Integer('HAD')
    commission_a = fields.Integer('Commission/Avances de Fonds')
    commission_t = fields.Integer('Commission de Transit')
    commission_d = fields.Integer('Commision/Débours')
    divers_inter = fields.Integer('Divers')
    total_int = fields.Integer('Total Interventions HT', compute='_compute_total_int')
    t_v_a_int = fields.Integer(string='TVA sur interventions', readonly=False)
    total_ttc = fields.Integer(string='Total Interventions TTC', compute='_compute_ttc')
    numero_dossier = fields.Char('Numero de dossier', compute='_compute_dossier')
    code_client = fields.Char('Code Client', compute='_compute_code_client')
    type_operation = fields.Char('Type d\'opération', compute='_compute_operation')
    note = fields.Text('Commentaires')

    #    @api.onchange('remise_had')
    #    def onchange_remise_had(self):
    #        self.h_a_d = self.real_had - ((self.real_had * self.remise_had) / 100)

    # REMISE HAD
    remise_had = fields.Float('Remise HAD')

    # REFERENCE FOURNISSEUR
    ref_p_f = fields.Char('Référence Proforma Fournisseur', compute='_compute_ref_fournisseur')
    ref_f_f = fields.Char('Référence Facture Fournisseur')

    # CONDITION VENTE
    condition_vente = fields.Boolean('Afficher conditions de règlement', default=True)

    # NET A PAYER
    n_a_p = fields.Integer(string='NET A PAYER', compute='_compute_nap')

    amount_total_letter = fields.Char('Montant total en lettre', required=False, compute='get_amount_letter')
