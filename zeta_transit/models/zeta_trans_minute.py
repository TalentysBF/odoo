# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import had
import math


class ZetaTransMinute(models.Model):
    _name = 'zeta.trans.minute'
    _description = 'Zeta Transit Minute'
    _inherit = ['ir.needaction_mixin']

    @api.model
    def decimales(self, f):
        if math.fabs(f - 0.0) > 1e-5:
            return f - math.floor(f)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('zeta.trans.minute') or '/'
        return super(ZetaTransMinute, self).create(vals)

    @api.model
    def _get_default_minute(self):
        return self.env['ir.sequence'].next_by_code('zeta.trans.minute')

    @api.multi
    def actualiser(self):
        self.onchange_amount_all()
        self.fill_back()
        self.onchange_dossier()
        self.onchange_compute_p_m_d()
        self.onchange_remise_had()

    @api.onchange('res_article_id')
    def onchange_amount_all(self):
        for article in self:
            int_final_dd = 0
            int_final_rs = 0
            int_final_pcs = 0
            int_final_pc = 0
            int_final_ri = 0
            int_final_pea = 0
            int_final_cpv = 0
            int_final_tva = 0
            int_final_tdt = 0
            int_final_aib = 0
            int_final_rsp = 0
            int_final_ttg = 0
            int_final_brut = 0
            for line in article.res_article_id:
                int_final_dd += line.d_d
                int_final_rs += line.statistique
                int_final_pcs += line.p_c_s
                int_final_ri += line.r_i
                int_final_pc += line.p_c
                int_final_pea += line.peage
                int_final_cpv += line.c_p_v
                int_final_tva += line.float_t_v_a
                int_final_tdt += line.total_droits
                int_final_aib += line.a_i_b
                int_final_rsp += line.remise_special
                int_final_ttg += line.total_taxes
                int_final_brut += line.int_poids_brut
            article.update({
                'int_final_dd': int_final_dd,
                'int_final_rs': int_final_rs,
                'int_final_pcs': int_final_pcs,
                'int_final_ri': int_final_ri,
                'int_final_pc': int_final_pc,
                'int_final_pea': int_final_pea,
                'int_final_cpv': int_final_cpv,
                'int_final_tva': int_final_tva,
                'int_final_tdt': int_final_tdt,
                'int_final_aib': int_final_aib,
                'int_final_rsp': int_final_rsp,
                'int_final_ttg': int_final_ttg,
                'int_final_brut': int_final_brut,
            })

    @api.onchange('res_article_id')
    def onchange_compute_article(self):
        for minute in self:
            nbr = 0
            for _ in minute.res_article_id:
                nbr += 1
            self.update({
                'article_number': nbr,
            })

    @api.depends('depend')
    @api.onchange('str_dossier')
    def onchange_dossier(self):
        if self.str_dossier:
            try:
                self.res_client = self.str_dossier.client
            except:
                pass

    @api.model
    def _get_default_avance(self):
        return self.env['ir.sequence'].next_by_code('zeta.trans.avance')

    @api.onchange('res_article_id')
    def fill_back(self):
        d_d = 0
        statistique = 0
        p_c_s = 0
        p_c = 0
        c_p_v = 0
        t_v_a_d = 0
        peage = 0
        r_s_p = 0
        r_i = 0
        a_i_b = 0
        assurance = 0
        honoraire = 0
        for article in self.res_article_id:
            d_d += article.d_d
            statistique += article.statistique
            p_c_s += article.p_c_s
            p_c += article.p_c
            c_p_v += article.c_p_v
            t_v_a_d += article.float_t_v_a
            peage += peage
            r_s_p += article.remise_special
            r_i += article.r_i
            a_i_b += article.a_i_b
            if article.bool_assurance:
                assurance += article.prime_total
            honoraire += article.honoraire
        self.update({
            'd_d': d_d,
            'statistique': statistique,
            'p_c_s': p_c_s,
            'p_c': p_c,
            'c_p_v': c_p_v,
            't_v_a_d': t_v_a_d,
            'peage': peage,
            'r_s_p': r_s_p,
            'r_i': r_i,
            'a_i_b': a_i_b,
            'assurance': assurance,
            'honoraire': honoraire
        })

    @api.depends('d_d', 'p_c', 'p_c_s', 'statistique', 't_v_a_d')
    def _compute_droits(self):
        self.t_d_d = self.d_d + self.statistique + self.p_c_s + self.p_c + self.c_p_v + self.t_v_a_d

    @api.depends('r_i', 'a_i_b', 'r_s_p')
    def _compute_total_taxes(self):
        self.t_d_t = self.r_i + self.a_i_b + self.r_s_p

    @api.depends('int_final_tdt', 'int_final_ttg')
    def _compute_m_total(self):
        self.m_total_d = self.int_final_tdt + self.int_final_ttg

    @api.onchange('p_m_d')
    def onchange_compute_p_m_d(self):
        if self.p_m_d in ['900', '1050', '2800', '4000']:
            value = self.int_final_brut if self.int_final_brut > 1000 else 1000
            if self.decimales(float(self.p_m_d) * (value / 1000)) >= 0.05:
                self.p_m_d_val = math.ceil((float(self.p_m_d) * value) / 1000)
            else:
                self.p_m_d_val = round((float(self.p_m_d) * value) / 1000)
        elif self.p_m_d in ['575', '1150', '1700', '2800', '8400', '12600', '21000', '35000', '63000']:
            value = 0
            for article in self.res_article_id:
                value += article.qte_complete
            self.p_m_d_val = int(self.p_m_d) * value
        else:
            self.p_m_d = 0

    @api.depends('p_m_d', 'p_m_d_val')
    def _compute_tva_1(self):
        if self.decimales((self.p_m_d_val * 18) / 100) >= 0.05:
            self.t_v_a_d_1 = math.ceil((float(self.p_m_d_val) * 18) / 100)
        else:
            self.t_v_a_d_1 = round((float(self.p_m_d_val) * 18) / 100)

    @api.depends('stationement')
    def _compute_tva_2(self):
        self.t_v_a_d_2 = math.ceil((self.stationement * 18) / 100)  # remove ceil

    @api.depends('t_s_ecor', 'vaccation', 'assurance', 't_v_a_d_1', 'camionage_value', 'decl_value', 'm_f_f',
                 'stationement', 't_v_a_d_2', 'douane_fg', 'divers_debours', 'm_r_d', 'p_m_d_val')
    def _compute_total_debours(self):
        self.total_debours = self.t_s_ecor + self.vaccation + self.assurance + self.t_v_a_d_1 + \
                             self.camionage_value + self.decl_value + self.m_f_f + self.stationement + \
                             self.t_v_a_d_2 + self.douane_fg + self.divers_debours + self.m_r_d + self.p_m_d_val

    @api.onchange('total_debours')
    def onchange_total_debours(self):
        self.total_debours_bis = self.total_debours

    @api.depends('total_ht')
    def _compute_tva_3(self):
        self.t_v_a_d_3 = round(float(self.total_ht * 18) / 100)

    @api.depends('divers_inter', 'honoraire', 'avance', 'transit', 'debours')
    def _compute_total_ht(self):
        self.total_ht = self.ouverture_d + self.imprime + self.honoraire + self.divers_inter + \
                        self.avance + self.transit + self.debours

    @api.depends('total_ht', 't_v_a_d_3')
    def _compute_total_ttc(self):
        self.total_ttc = self.total_ht + self.t_v_a_d_3

    @api.depends('m_total_d', 'avance_taux')
    def _compute_avance(self):
        self.avance = round(float(self.m_total_d * self.avance_taux) / 100)

    @api.depends('m_total_d', 'transit_taux')
    def _compute_transit(self):
        val = round((float(self.fin_caf) * float(self.transit_taux)) / 100)
        self.transit = val if val <= 16000 else 16000

    @api.depends('total_debours', 'debours_taux')
    def _compute_com_debours(self):
        self.debours = round((float(self.total_debours) * float(self.debours_taux)) / 100)

    @api.depends('res_article_id')
    def _compute_fin_caf(self):
        for minute in self:
            caf = 0
            for article in minute.res_article_id:
                caf += article.valeur_caf
            minute.fin_caf = caf

    @api.onchange('remise_had')
    def onchange_remise_had(self):
        self.honoraire = self.honoraire - ((self.honoraire * self.remise_had) / 100)

    name = fields.Char(default='Nouveau', required=True, string='Minute', index=True, copy=False)
    a_name = fields.Char('Avance', default=_get_default_avance)
    article_number = fields.Integer('Nombre D\'article(s)')
    str_dossier = fields.Many2one('zeta.trans.dossier', 'Dossier N°.', required=True)
    res_client = fields.Many2one('res.partner', 'Client')
    date_date = fields.Date('Date', default=fields.Datetime.now())
    res_article_id = fields.One2many('zeta.trans.minute.article', 'minute_id', 'Article', copy=True, store=True)

    int_final_dd = fields.Integer(string='Droits de douane')
    int_final_rs = fields.Integer(string='Redevance statistique')
    int_final_pcs = fields.Integer(string='PCS')
    int_final_pc = fields.Integer(string='PC')
    int_final_pea = fields.Integer(string='PEA')
    int_final_cpv = fields.Integer(string='CPV')
    int_final_tva = fields.Integer(string='TVA')
    int_final_tdt = fields.Integer(string='TOTAL DES DROITS')

    int_final_ri = fields.Integer(string='RI')
    int_final_aib = fields.Integer(string='AIB')
    int_final_rsp = fields.Integer(string='RSP')
    int_final_ttg = fields.Integer(string='TOTAL DES TAXES', store=True)

    int_final_brut = fields.Float(string="Poids Brut")

    # DROITS
    d_d = fields.Integer('D.D')
    statistique = fields.Integer('Statistique')
    p_c_s = fields.Integer('P.C.S')
    p_c = fields.Integer('P.C')
    c_p_v = fields.Integer('C.P.V')

    # TAXES
    r_i = fields.Integer('R.I')
    t_v_a_d = fields.Integer('T.V.A')
    peage = fields.Integer('Peage')
    t_d_d = fields.Integer(string='Total Des Droits', compute='_compute_droits')

    r_s_p = fields.Integer('R.S.P')
    a_i_b = fields.Integer('A.I.B')
    t_d_t = fields.Integer(sting='Total Des Taxes', compute='_compute_total_taxes')
    m_total_d = fields.Integer(string='TOTAL AVANCE DE FONDS',
                               compute='_compute_m_total')

    # DEBOURS
    t_s_ecor = fields.Integer('T.S ECOR')
    vaccation = fields.Integer('Vacation')
    assurance = fields.Integer('Assurance')
    p_m_d = fields.Selection([('0', '0'), ('575', '575F/U'), ('900', '900F/Tone'), ('1050', '1050F/Tone'),
                              ('1150', '1150F/U'), ('1700', '1700F/U'), ('2800', '2800F/Tone'), ('4000', '4000F/Tone'),
                              ('8400', '8400F/U'), ('12600', '12600F/U'), ('21000', '21000F/U'), ('35000', '35000F/U'),
                              ('63000', '63000F/U')], 'Passage Mag.S/Douane')
    p_m_d_val = fields.Integer('Valeur p_m_d')
    t_v_a_d_1 = fields.Integer(string='TVA', compute='_compute_tva_1')
    camionage = fields.Selection([('c', 'Camionage'), ('m', 'Manutention'), ('c_m', 'Camionage Et Manutantion')])
    camionage_value = fields.Integer()
    rem_doc = fields.Char('Nom Remise Doc')

    decl_douane = fields.Selection(
        [('decl', 'Decl De Douane Unique'), ('laboratoire', 'Laboratoire'), ('phyto', 'Phyto'),
         ('certif', 'Certif.Vete'), ('autres', 'Autres')], 'Decl de Douane unique')
    decl_value = fields.Integer('Valeur')
    f_f_n = fields.Char('Facture Frontière N°.')
    m_f_f = fields.Integer('Montant Facture Frontière')
    stationement = fields.Integer('Stationnement')
    t_v_a_d_2 = fields.Integer(string='TVA', compute='_compute_tva_2')
    douane_fg = fields.Integer('Douane FG')
    divers_debours = fields.Integer('Divers')
    m_r_d = fields.Integer('Montant Remise Doc')
    total_debours = fields.Integer(string='Total Debours', compute='_compute_total_debours')
    total_debours_bis = fields.Integer(string='Total Debours')

    # REMISE HAD
    remise_had = fields.Float('Remise HAD')
    h_a_d = fields.Integer('HAD')

    # INTERVENTIONS
    ouverture_d = fields.Integer(string='Ouverture de dossier', default=5250)
    imprime = fields.Integer(string='Imprimés et Timbres', default=9000)
    fin_caf = fields.Integer(string='Total CAF', compute='_compute_fin_caf', store=True)
    honoraire = fields.Integer('H.A.D', readonly=False)
    divers_inter = fields.Integer('Divers')
    total_ht = fields.Integer(string='Total HT', compute='_compute_total_ht')
    avance = fields.Integer(string='Avance de fonds', compute='_compute_avance')
    avance_taux = fields.Float('Avance Taux', default=4.95)
    transit = fields.Float(string='Transit', compute='_compute_transit', store=True)
    transit_taux = fields.Float('Transit Taux', default=0.2)
    debours = fields.Integer('Débours', compute='_compute_com_debours')
    debours_taux = fields.Float('Débours Taux', default=4)
    t_v_a_d_3 = fields.Integer(string='TVA 18%', compute='_compute_tva_3')
    total_ttc = fields.Integer(string='Total Intervention T.T.C', compute='_compute_total_ttc')


class ZetaTransMinuteArticle(models.Model):
    _name = 'zeta.trans.minute.article'
    _description = 'Zeta Transit Minute Article'

    @api.multi
    def _compute_ri(self):
        for article in self:
            article.r_i = article.minute_id.article_number + 1

    @api.model
    def decimales(self, f):
        if math.fabs(f - 0.0) > 1e-5:
            return f - math.floor(f)

    @api.depends('int_valeur_fob_1', 'int_valeur_fob_2', 'assurance', 'int_valeur_fret', 'autres_frais')
    def _compute_caf(self):
        for line in self:
            line.valeur_caf = line.int_valeur_fob_1 + line.int_valeur_fob_2 \
                              + line.assurance + line.int_valeur_fret + line.autres_frais

    @api.depends('prime_total')
    def _compute_assurance(self):
        for line in self:
            line.assurance = line.prime_total

    @api.depends('valeur_caf', 'taux')
    def _compute_p_nette(self):
        for line in self:
            line.prime_net = round(((line.int_valeur_fob_1 + line.int_valeur_fob_2) * line.taux) / 100)

    @api.depends('prime_net', 'cout_acte', 'taxes_taux')
    def _compute_taxe(self):
        for line in self:
            line.taxes = round(((line.prime_net + line.cout_acte) * float(line.taxes_taux)) / 100)

    @api.depends('prime_net')
    def _compute_cout_acte(self):
        for line in self:
            if line.prime_net < 500000:
                line.cout_acte = 1000
            else:
                line.cout_acte = 2000

    @api.depends('prime_net', 'cout_acte', 'taxes')
    def _compute_p_total(self):
        for line in self:
            line.prime_total = line.prime_net + line.cout_acte + line.taxes

    @api.depends('valeur_caf', 'regime')
    def _compute_statistique(self):
        for line in self:
            if (line.regime == 'u_a_t' or line.regime == 'u_s_t' or
                        line.minute_id.str_dossier.type_operation == 'export'):
                line.statistique = 0
            else:
                value = float(line.valeur_caf) / 100
                if self.decimales(value) >= 0.05:
                    line.statistique = math.ceil(value)
                else:
                    line.statistique = round(value)

    @api.depends('categorie', 'regime')
    def _compute_dd(self):
        for line in self:
            if (line.regime == 'u_a_t' or line.regime == 'u_s_t' or int(
                    line.categorie) == 0 or line.minute_id.str_dossier.type_operation == 'export'):
                line.d_d = 0
            elif int(line.categorie) == 1:
                if line.valeur_caf > 0:
                    if self.decimales((float(line.valeur_caf) * 5) / 100) >= 0.05:
                        line.d_d = math.ceil((float(line.valeur_caf) * 5) / 100)
                    else:
                        line.d_d = round(float(line.valeur_caf) * 5) / 100
                else:
                    if self.decimales((float(line.valeur_mercurial) * 5) / 100) >= 0.05:
                        line.d_d = math.ceil((float(line.valeur_mercurial) * 5) / 100)
                    else:
                        line.d_d = round(float(line.valeur_mercurial * 5) / 100)
            elif int(line.categorie) == 2:
                if line.valeur_caf > 0:
                    if self.decimales((float(line.valeur_caf) * 10) / 100) >= 0.05:
                        line.d_d = math.ceil((float(line.valeur_caf) * 10) / 100)
                    else:
                        line.d_d = round((float(line.valeur_caf) * 10) / 100)
                else:
                    if self.decimales((float(line.valeur_mercurial) * 10) / 100) >= 0.05:
                        line.d_d = math.ceil((float(line.valeur_mercurial) * 10) / 100)
                    else:
                        line.d_d = round(float(line.valeur_mercurial) * 10) / 100
            elif int(line.categorie) == 3:
                if line.valeur_caf > 0:
                    if self.decimales((float(line.valeur_caf) * 20) / 100) >= 0.05:
                        line.d_d = math.ceil((float(line.valeur_caf) * 20) / 100)
                    else:
                        line.d_d = round(float(line.valeur_caf) * 20) / 100
                else:
                    if self.decimales((float(line.valeur_mercurial) * 20) / 100) >= 0.05:
                        line.d_d = math.ceil((float(line.valeur_mercurial) * 20) / 100)
                    else:
                        line.d_d = round(float(line.valeur_mercurial) * 20) / 100
            elif int(line.categorie) == 4:
                if line.valeur_caf > 0:
                    if self.decimales((float(line.valeur_caf) * 35) / 100) >= 0.05:
                        line.d_d = math.ceil((float(line.valeur_caf) * 35) / 100)
                    else:
                        line.d_d = round((float(line.valeur_caf) * 35) / 100)
                else:
                    if self.decimales((float(line.valeur_mercurial) * 35) / 100) >= 0.05:
                        line.d_d = math.ceil((float(line.valeur_mercurial) * 35) / 100)
                    else:
                        line.d_d = round((float(line.valeur_mercurial) * 35) / 100)

    @api.depends('valeur_caf', 'valeur_mercurial', 'regime', 'p_c_s_value')
    def _compute_pcs(self):
        for line in self:
            pcs_value = float(line.p_c_s_value)
            if line.regime == 'u_a_t' or line.regime == 'u_s_t' or \
                            line.regime == 'u_na_t' or line.regime == 'u_ns_t' or \
                            line.minute_id.str_dossier.type_operation == 'export':
                line.p_c_s = 0
            elif line.valeur_caf > 0:
                if self.decimales(float(line.valeur_caf) * pcs_value) >= 0.05:
                    line.p_c_s = math.ceil(float(line.valeur_caf) * pcs_value)
                else:
                    line.p_c_s = round(float(line.valeur_caf) * pcs_value)
            else:
                if self.decimales(float(line.valeur_mercurial) * pcs_value) >= 0.05:
                    line.p_c_s = math.ceil(float(line.valeur_mercurial) * pcs_value)
                else:
                    line.p_c_s = round(float(line.valeur_mercurial) * pcs_value)

    @api.depends('valeur_caf', 'valeur_mercurial', 'regime')
    def _compute_pc(self):
        for line in self:
            if (line.regime == 'u_a_t' or line.regime == 'u_s_t' or
                        line.regime == 'u_na_t' or line.regime == 'u_ns_t' or
                        line.minute_id.str_dossier.type_operation == 'export'):
                line.p_c = 0
            elif line.valeur_caf > 0:
                value = (float(line.valeur_caf) * 5) / 1000
                if self.decimales(value) >= 0.05:
                    line.p_c = math.ceil(value)
                else:
                    line.p_c = round(value)
            else:
                value = (float(line.valeur_mercurial) * 5) / 1000
                if self.decimales(value) >= 0.05:
                    line.p_c = math.ceil(value)
                else:
                    line.p_c = round(value)

    @api.depends('int_valeur_fob_1', 'int_valeur_fob_2')
    def _compute_cpv(self):
        for line in self:
            if line.minute_id.str_dossier.type_operation == 'export':
                line.c_p_v = 0
            elif line.int_valeur_fob_1 > 0:
                value = (float(line.int_valeur_fob_1)) / 100
                if self.decimales(value) >= 0.05:
                    line.c_p_v = math.ceil(value)
                else:
                    line.c_p_v = round(value)

    @api.depends('valeur_caf', 'd_d', 'statistique', 'p_c', 'p_c_s', 'regime')
    def _compute_tva(self):
        for line in self:
            if line.regime == 'u_s_t' or line.regime == 'u_ns_t' or \
                            line.minute_id.str_dossier.type_operation == 'export' or \
                    not line.count_tva:
                line.float_t_v_a = 0
            else:
                value = (float(line.valeur_caf + line.d_d + line.statistique + line.p_c + line.p_c_s) * 18) / 100
                if self.decimales(value) >= 0.05:
                    line.float_t_v_a = math.ceil(value)
                else:
                    line.float_t_v_a = round(value)

    @api.depends('d_d', 'statistique', 'p_c_s', 'peage', 'c_p_v', 'float_t_v_a', 'p_c')
    def _compute_total_droits(self):
        for line in self:
            line.total_droits = line.d_d + line.statistique + line.p_c_s + line.peage + line.c_p_v + \
                                line.float_t_v_a + line.p_c

    @api.depends('a_i_b_select')
    def _compute_aib(self):
        for line in self:
            value = (float(line.total_droits + line.valeur_caf) * float(line.a_i_b_select)) / 100
            if self.decimales(value) >= 0.05:
                line.a_i_b = math.ceil(value)
            else:
                line.a_i_b = round(value)

    @api.depends('total_droits', 'r_i', 'a_i_b')
    @api.onchange('remise_val')
    def onchange_compute_remise(self):
        for line in self:
            value = (float(line.total_droits + line.r_i + line.a_i_b) * float(line.remise_val)) / 1000
            if self.decimales(value) >= 0.1:
                line.remise_special = math.ceil(value)
            else:
                line.remise_special = round(value)

    @api.depends('r_i', 'a_i_b', 'remise_special')
    def _compute_taxes(self):
        for line in self:
            line.total_taxes = line.r_i + line.a_i_b + line.remise_special

    @api.depends('total_droits', 'total_taxes')
    def _compute_droits_taxes(self):
        for line in self:
            line.droits_taxes = line.total_droits + line.total_taxes

    @api.onchange('peage_comp', 'int_poids_brut')
    def _compute_peage(self):
        for line in self:
            if line.minute_id.str_dossier.type_operation == 'export':
                line.peage = 0
            elif line.peage_comp != '3000':
                value = float(line.peage_comp) * line.int_poids_brut
                if self.decimales(value) >= 0.05:
                    line.peage = math.ceil(value)
                else:
                    line.peage = round(value)
            else:
                value = 3000 * float(line.qte_complete)
                if self.decimales(value):
                    line.peage = math.ceil(value)
                else:
                    line.peage = round(value)

    @api.onchange('secteur')
    def compute_had(self):
        for line in self:
            if line.secteur != '0':
                line.honoraire = had.compute_had(int(line.secteur), line.valeur_caf)

    @api.onchange('int_valeur_fob_2')
    def onchange_fob_2(self):
        if self.int_valeur_fob_2 > 0:
            self.c_p_v = 0
            self.int_valeur_fob_1 = 0

    @api.onchange('int_valeur_fob_1')
    def onchange_fob_1(self):
        if self.int_valeur_fob_1 > 0:
            self.int_valeur_fob_2 = 0

    # LINK
    name = fields.Char('Libelle')

    minute_id = fields.Many2one('zeta.trans.minute', 'Minute ID', store=True)

    # DETAIL MARCHANDISE
    res_origine = fields.Many2one('res.country', 'Origine')
    str_provenance = fields.Many2one('res.country', 'Provenance')
    str_n_t_s = fields.Char('NTS')
    qte_complete = fields.Integer('Quantité complète')
    nbr_colis = fields.Integer('Nombre de colis', required=True)
    int_poids_net = fields.Float('Poids Net', required=True)
    int_poids_brut = fields.Float('Poids Brut', required=True)
    int_valeur_fob_1 = fields.Integer('Valeur FOB 1')
    int_valeur_fob_2 = fields.Integer('Valeur FOB 2')
    res_devise = fields.Many2one('res.currency', 'Devise', default=42)
    int_valeur_devise = fields.Float('Valeur Devise')
    int_valeur_fret = fields.Integer('Valeur Fret', required=True)
    assurance = fields.Integer('Assurance', required=True)
    bool_assurance = fields.Boolean('Inclure Assurance', default=False)
    autres_frais = fields.Integer('Autres frais', required=True)
    valeur_caf = fields.Integer(string='VALEUR CAF', compute='_compute_caf', store=True)
    valeur_mercurial = fields.Integer('VALEUR MERCURIALE')

    # TARIF A APPLIQUE
    regime = fields.Selection([('t_e_c', 'Tarif Extérieur Commun'),
                               ('u_a_t', 'Uemoa agréé avec TVA'),
                               ('u_s_t', 'Uemoa agréé sans TVA'),
                               ('u_na_t', 'Uemoa non agréé avec TVA'),
                               ('u_ns_t', 'Uemoa non agréé sans TVA'),
                               ('autre', 'Autres Régime')],
                              string='Régime', required=True)

    categorie = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], 'Catégorie',
                                 required=True)
    facturer = fields.Boolean('Facturer Droits & Taxes', default=True)
    certif_id = fields.Boolean('Certificat D\'origine UEMOA')
    count_tva = fields.Boolean('TVA', default=True)

    # ASSURANCE DE DOUANE
    taux = fields.Float(string='Taux', required=True, default=0.40)
    prime_net = fields.Float(string='Prime Nette', compute='_compute_p_nette')
    cout_acte = fields.Float(string='Côut d\'acte', default=5000)
    taxes = fields.Float(string='Taxes', compute='_compute_taxe')
    taxes_taux = fields.Float(string='Taxes', default=0.8)
    prime_total = fields.Float(string='Prime Total', compute='_compute_p_total', store=True)

    # DROITS DE DOUANE
    d_d = fields.Integer(string='D.D', compute='_compute_dd', readonly=False, store=True)
    statistique = fields.Integer(string='Statistique', compute='_compute_statistique', readonly=False, store=True)
    p_c_s = fields.Float(string='PCS', compute='_compute_pcs', readonly=False, store=True)
    p_c_s_value = fields.Selection([('0.008', '0.8'), ('0.01', '1')], required=True)
    p_c = fields.Float(string='PC', compute='_compute_pc', readonly=False, store=True)
    c_p_v = fields.Float(string='CPV', compute='_compute_cpv', readonly=False, store=True)
    float_t_v_a = fields.Integer(string='TVA', compute='_compute_tva', readonly=False, store=True)
    peage_comp = fields.Selection([('0', '0'), ('0.5', '0.5F/KG'), ('0.075', '0.075F/KG'), ('3000', '3000F')], 'Peage',
                                  required=True)
    peage = fields.Integer("Peage")
    total_droits = fields.Integer(string='Total des Droits', compute='_compute_total_droits', store=True)

    # TAXES
    r_i = fields.Integer(string='R.I', default=0, required=True)
    a_i_b_select = fields.Selection([('1', '1'), ('2', '2')], string='A.I.B', store=True)
    a_i_b = fields.Float(string='A.I.B Valeur', store=True, compute='_compute_aib')
    remise_special = fields.Float(string='Remise Spéciale', store=True)
    remise_val = fields.Selection([('0', '0'), ('1', '1')], string='Valeur remise')
    total_taxes = fields.Float(string='Total des Taxes', compute='_compute_taxes', store=True)

    # TOTAL DROITS ET TAXES
    droits_taxes = fields.Integer('Total des Droits et Taxes', compute='_compute_droits_taxes')

    honoraire = fields.Integer('H.A.D', readonly=False)
    secteur = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')],
                               string='Section', default='0')
