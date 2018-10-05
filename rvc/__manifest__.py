# -*- coding: utf-8 -*-
{
    'name': "RVC",
    'summary': """Talentys rapport de visite client """,
    'description': """ Rapport de Visite Client""",
    'author': "Talentys",
    'website': "http://www.talentys.bf",
    'category': 'Application',
    'version': '0.1',
    'depends': ['base','calendar'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True
}
