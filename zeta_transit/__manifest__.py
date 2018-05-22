# -*- coding: utf-8 -*-
{
    'name': "ZETA TRANSIT",

    'summary': "SOTRACI Gescom Transit",

    'description': """
        Simple application From ZETA to SOTRACI Gescom Transit
    """,

    'author': "Zeta",
    'website': "http://www.zeta-bf.com",

    'category': 'Application',
    'version': '0.1',
    'depends': ['base'],

    'data': [
        'security/zeta_trans.xml',
        'security/ir.model.access.csv',
        'security/zeta_trans.xml',
        'views/zeta_trans_company.xml',
        'views/custom_template.xml',
        'views/zeta_trans_dossier.xml',
        'data/zeta_transit_sequence.xml',
        'views/zeta_trans_minute.xml',
        'views/zeta_trans_proforma.xml',
        'views/zeta_trans_facture.xml',
        'views/zeta_trans_caisse_kanban.xml',
        'views/zeta_trans_caisse.xml',
        'views/zeta_trans_transaction.xml',
        'views/zeta_trans_client.xml',
        'views/zeta_trans_had.xml',
        'reports/zeta_trans_minute_report.xml',
        'reports/zeta_trans_proforma_report.xml',
        'reports/zeta_trans_facture_report.xml',
        'views/zeta_trans_report.xml',
        #'data/zeta_trans_demo.yml',
    ],

    #'demo': [
    #    'data/zeta_trans_demo.yml',
    #],

    'instalable': True,
    'application': True,
}