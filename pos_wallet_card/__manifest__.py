# -*- coding: utf-8 -*-
{
    'name': 'POS Customer Wallet',
    'live_test_url': 'http://posodoo.com/web/signup',
    'version': '1.1.3',
    'category': 'Point of Sale',
    'sequence': 0,
    'author': 'TL Technology',
    'website': 'http://posodoo.com',
    'price': '50',
    'description': 'Give change amount of customers when customers payment order and allow customers use wallet card',
    "currency": 'EUR',
    'depends': ['point_of_sale'],
    'data': [
        'template/import.xml',
        'views/account_journal.xml',
        'views/res_partner.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
    'images': ['static/description/icon.png'],
    'support': 'thanhchatvn@gmail.com'
}
