# -*- coding: utf-8 -*-
{
    'name': "Reclamation",  

    'summary': """une premiere version du module Agence""",

    'description': """
        A detailed description of what your module does.
        - It will depend on `base`, `project`, and `survey` modules
        - You can add more information here
    """,

    'author': "GUEFAIFIA Rania",  
    'website': "http://www.yourcompany.com",  

    # Categories can be used to filter modules in modules listing
    'category': 'Your Category',  
    'version': '0.2',  

    # Declare the dependencies
    'depends': ['base', 'project', 'survey','website','mail'],  

    # Always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/agence.xml',
        'data/emailt.xml',

    ],

    # Only loaded in demonstration mode
    # no demo data pour linstant
}
