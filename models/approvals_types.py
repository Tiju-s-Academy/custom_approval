# -*- coding: utf-8 -*-
from odoo import models, fields


class ApprovalsTypes(models.Model):
    """ this model is used for store approval types"""
    _name = 'approvals.types'
    _description = 'Approval Types'
    _rec_name = 'approvals_type'
    _inherit = 'mail.thread'

    approvals_type = fields.Char(string='Approvals Type')
    approval_image = fields.Binary(string='Approval Image')
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company',default=lambda self:self.env.company)
    approver_ids = fields.One2many('approval.type.approver', 'approval_type_id', string='Approvers')