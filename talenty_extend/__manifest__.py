# -*- coding: utf-8 -*-
{
    'name': 'Talentys Extend',
    'version': '1.0',
    'website': 'https://www.talentys.bf',
    'description': "Simple Talentys Extend",
    'depends': ['sale', 'purchase', 'account_invoicing', 'crm', 'sale_margin'],
    'data': [
        'views/account.xml',
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/crm_lead.xml',
        'report/sale_report_template.xml',
        'report/account_invoice_report.xml',
        'report/purchase_template.xml',
        'security/talentys_extend.xml'
    ],
    'installable': True,
    'application': True
}
