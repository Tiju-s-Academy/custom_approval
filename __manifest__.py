{
    'name': 'Approvals',
    'version': '17.0.1.0.0',
    'summary': 'A comprehensive module to manage Approvals from the Managers',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'data/activity.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'views/approvals_types_view.xml',
        'views/approval_request.xml',
        'wizard/hold_request_wizard.xml',
        'views/custom_approvals_menu.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}

