{
    'name': 'Custom Sale',
    'summary': 'Adds a private logistics tab on quotes',
    'description': 'Allows recording private technical notes on quotes for logistics, not visible to the client.',
    'version': '1.1.0',
    'category': 'Sales',
    'author': 'Nexyor',
    'depends': ['sale', 'sale_renting', 'product', 'maintenance'],
    'data': [
        'data/res_groups.xml',
        'views/sale_order_views.xml',
        'reports/sheet_road_report.xml',
        'reports/sheet_road_template.xml',
        'views/stock_views.xml',

        
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
