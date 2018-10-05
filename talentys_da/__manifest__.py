# -*- coding: utf-8 -*-

{
    'name': 'Talentys DA',
    'version': '0.9.3',
    'website': 'https://www.talentys.bf',
    'description': "Talentys Demande d'achat",
    'depends': ['sale', 'purchase', 'account_invoicing', 'crm', 'sale_margin'],
    'data': [
        'security/talentys_da.xml',
        'views/payment_cash.xml',
        'views/demande_achat.xml',
        'views/res_user.xml',
        'data/sequence.xml',
		'reports/report_talentys_da.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True
}
