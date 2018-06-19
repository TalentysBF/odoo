# -*- coding: utf-8 -*-

{
    'name': 'Talentys DA',
    'version': '0.9.3',
    'website': 'https://www.talentys.bf',
    'description': "Talentys Demande d'achat",
    'depends': ['sale', 'purchase', 'account_invoicing', 'crm', 'sale_margin'],
    'data': [
        'views/payment_cash.xml',
        'views/demande_achat.xml',
        'views/res_user.xml',
        'data/sequence.xml'
    ],
    'installable': True,
    'application': True
}
