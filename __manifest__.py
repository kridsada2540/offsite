{
    'name': "Offsite",

    'summary': """ """,

    'description': """

    """,

    'author': "Eduard Ojer",
    'website': "https://www.bru.ac.th/",
    'version': '0.1',

    'depends': ['base',
                'board',
                'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/offsite.xml',
        # 'views/expenses_board.xml',
        'views/partner.xml',
        'reports/report.xml',
    ],
}