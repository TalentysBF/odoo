# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ZetaTransAvance(models.Model):
	_name = 'zeta.trans.avance'


	@api.depends('str_minute')
	@api.onchange('str_minute')
	def fill_back(self):
		d_d = 0
		statistique = 0
		p_c_s = 0
		p_c =  0
		c_p_v = 0
		t_v_a_d = 0
		peage = 0
		r_s_p = 0
		r_i = 0
		a_i_b = 0
		assurance = 0
		for article in self.str_minute.res_article_id:
			d_d += article.d_d
			statistique += article.statistique
			p_c_s += article.p_c_s
			p_c += article.p_c
			c_p_v += article.c_p_v
			t_v_a_d += article.float_t_v_a
			peage += float(article.peage) * article.int_poids_net
			r_s_p += article.remise_special
			r_i += article.r_i
			a_i_b += article.a_i_b
			assurance += article.assurance
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
			'assurance': assurance
		})


	@api.depends('d_d','p_c','p_c_s','statistique','t_v_a_d')
	def _compute_droits(self):
		self.t_d_d = self.d_d + self.statistique + self.p_c_s + self.p_c + self.c_p_v + self.t_v_a_d

	@api.depends('r_i','a_i_b','r_s_p')
	def _compute_total_taxes(self):
		self.t_d_t = self.r_i + self.a_i_b + self.r_s_p

	@api.depends('t_d_t')
	def _compute_m_total(self):
		self.m_total_d = self.t_d_d + self.t_d_t

	@api.depends('p_m_d')
	def _compute_tva_1(self):
		self.t_v_a_d_1 = (float(self.p_m_d) * 18) / 100

	@api.depends('stationement')
	def _compute_tva_2(self):
		self.t_v_a_d_2 = (self.stationement * 18) / 100

	@api.depends('t_s_ecor','vaccation','assurance','t_v_a_d_1','camionage_value','decl_value','m_f_f','stationement','t_v_a_d_2','douane_fg','divers','m_r_d')
	def _compute_total_debours(self):
		passage = 0
		for article in self.str_minute.res_article_id:
			passage += float(article.int_poids_net / 1000) * float(self.p_m_d)
		self.total_debours = self.t_s_ecor + self.vaccation + self.assurance + passage + self.t_v_a_d_1 + self.camionage_value + self.decl_value + self.m_f_f + self.stationement + self.t_v_a_d_2 + self.douane_fg + self.divers + self.m_r_d

	@api.depends('total_ht')
	def _compute_tva_3(self):
		self.t_v_a_d_3 = (self.total_ht * 18) / 100

	@api.depends('divers','honoraire','avance','transit','debours')
	def _compute_total_ht(self):
		self.total_ht = self.ouverture_d + self.imprime +  self.honoraire + self.divers + self.avance + self.transit + self.debours

	@api.depends('total_ht','t_v_a_d_3')
	def _compute_total_ttc(self):
		self.total_ttc = self.total_ht + self.t_v_a_d_3

	@api.depends('m_total_d')
	def _compute_avance(self):
		self.avance = (self.m_total_d * 4.95) / 100

	@api.model
	def _compute_transit(self):
		caf = 0
		for article in self.str_minute.res_article_id:
			caf += article.valeur_caf
		self.transit = (caf * 0.2) / 100

	@api.model
	def _get_default_avance(self):
		return self.env['ir.sequence'].next_by_code('zeta.trans.avance')

	test = fields.Char('Test')
	name = fields.Char('Avance',default=_get_default_avance)
	str_minute = fields.Many2one('zeta.trans.minute','Minute')

	# DROIT
	d_d = fields.Integer('D.D')
	statistique = fields.Integer('Statistique')
	p_c_s = fields.Integer('P.C.S')
	p_c = fields.Integer('P.C')
	c_p_v = fields.Integer('C.P.V')
	t_v_a_d = fields.Integer('T.V.A')
	peage = fields.Integer('Peage')
	t_d_d = fields.Integer(string='Total Des Droits',readonly=True,compute='_compute_droits')

	# TAXES
	r_i = fields.Integer('R.I')
	r_s_p = fields.Integer('R.S.P')
	a_i_b = fields.Integer('A.I.B')
	t_d_t = fields.Integer(sting='Total Des Taxes',readonly=True,compute='_compute_total_taxes')
	m_total_d = fields.Integer(string='Montant Total liquide pour la declaration',readonly=True,compute='_compute_m_total')

	#DEBOURS
	t_s_ecor = fields.Integer('T.S.ECOR')
	vaccation = fields.Integer('Vacation')
	assurance = fields.Integer('Assurance')
	p_m_d = fields.Selection([('900','900F/Tone'),('1050','1050F/Tone'),('4000','4000F/Tone')],'Passage Mag.S/Douane')
	t_v_a_d_1 = fields.Integer(string='TVA',readonly=True,compute='_compute_tva_1')
	camionage = fields.Selection([('c','Camionage'),('m','Manutention'),('c_m','Camionage Et Manutantion')],'Camionage')
	camionage_value = fields.Integer('Valeur')
	rem_doc = fields.Char('Remise Doc')
	decl_douane = fields.Selection([('decl','Decl De Douane Unique'),('laboratoire','Laboratoire'),('phyto','Phyto'),('certif','Certif.Vete'),('autres','Autres')],'Decl de Douane unique')
	decl_value = fields.Integer('Valeur')
	f_f_n = fields.Char('Facture Frontiere N.')
	m_f_f = fields.Integer('Montant Facture Frontiere')
	stationement = fields.Integer('Stationement')
	t_v_a_d_2 = fields.Integer(string='TVA',readonly=True,compute='_compute_tva_2')
	douane_fg = fields.Integer('Douane FG')
	divers = fields.Integer('Divers')
	m_r_d = fields.Integer('Montant Remise Doc')
	total_debours = fields.Integer(string='Total Debours',readonly=True,compute='_compute_total_debours')

	#INTERVENTIONS
	ouverture_d = fields.Integer(string='Ouverture de dossier',readonly=True,default=5250)
	imprime = fields.Integer(string='Imprime et timbres',readonly=True,default=9000)
	honoraire = fields.Integer('Honoraire Des agree en douane H.A.D')
	divers = fields.Integer('Divers')
	total_ht = fields.Integer(string='Total HT',readonly=True,compute='_compute_total_ht')
	avance = fields.Integer(string='Avance de fonds',readonly=True,compute='_compute_avance')
	transit = fields.Float(string='Transit',readonly=True,compute='_compute_transit')
	debours = fields.Integer(string='Debours')
	t_v_a_d_3 = fields.Integer(string='TVA 18%',readonly=True,compute='_compute_tva_3')
	total_ttc = fields.Integer(string='Total Intervantion T.T.C',readonly=True,compute='_compute_total_ttc')
