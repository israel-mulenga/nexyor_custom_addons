{
    'name': 'Nexyor Team Management',
    'version': '1.0.0',
    'summary': 'Event Team Management and Conflict Detection for Nexyor SARLU',
    'description': """
        Custom Odoo module for managing operational teams and detecting schedule conflicts.
        Features:
        - Named operational teams with Team Leaders
        - Automatic user assignment from team members
        - Strict schedule conflict validation
        - Team Leader specific access rights
    """,
    'category': 'Project',
    'author': 'Nexyor SARLU',
    'depends': ['project', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/nexyor_team_security.xml',
        'views/nexyor_team_views.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
