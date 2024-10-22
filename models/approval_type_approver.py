# -*- coding: utf-8 -*-
from odoo import models, fields


class ApprovalTypeApprover(models.Model):
    """ its  approvers model """
    _name = 'approval.type.approver'
    _description = 'Approver'
    _inherit = 'mail.thread'

    approver_id = fields.Many2one('res.users', string='Approver', required=True)
    approval_type_id = fields.Many2one('approvals.types', string='Approval Type')
    required = fields.Boolean(string='Is Required?', help="Check this box if the approver's approval is required.")
    sequence = fields.Integer(string='Sequence', default=10, help="Defines the order of approval.")
    is_approved = fields.Boolean(string="Is Approved?", default=False,
                                 help="Check this box if the approver has approved.")