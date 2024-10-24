# -*- coding: utf-8 -*-
from odoo import models, fields,api


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
    approved_request_count = fields.Integer(string='Approved Requests', compute='_compute_request_counts')
    rejected_request_count = fields.Integer(string='Rejected Requests', compute='_compute_request_counts')
    to_review_request_count = fields.Integer(string='To Review Requests', compute='_compute_request_counts')

    @api.depends('approvals_type')
    def _compute_request_counts(self):
        for record in self:
            # Count approved requests
            approved_requests = self.env['approval.request'].search_count([
                ('approval_type_id', '=', record.id),
                ('state', '=', 'approved')  # Assuming 'approved' is the state for approved requests
            ])
            record.approved_request_count = approved_requests

            # Count rejected requests
            rejected_requests = self.env['approval.request'].search_count([
                ('approval_type_id', '=', record.id),
                ('state', '=', 'rejected')  # Assuming 'rejected' is the state for rejected requests
            ])
            record.rejected_request_count = rejected_requests

            # Count "To Review" (submitted) requests
            to_review_requests = self.env['approval.request'].search_count([
                ('approval_type_id', '=', record.id),
                ('state', '=', 'submitted')  # Assuming 'submitted' is the state for reviewable requests
            ])
            record.to_review_request_count = to_review_requests
    def action_new_approval_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'approval.request',
            'target': 'new',  # This opens the form in a new modal window.
            'context': {
                'default_approval_type_id': self.id,  # Passing the current approval type ID to the form
                'create': True,
        }
    }
    def action_get_approval_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Requests',
            'view_mode': 'kanban,form',
            'res_model': 'approval.request',
            'domain': [('approval_type_id', '=', self.id)],
            'create': True
            }

    def btn1(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Requests',
            'view_mode': 'kanban',
            'res_model': 'approval.request',
            'domain': ['&', ('approval_type_id', '=', self.id), ('state', '=', 'approved')],
            'create': True
        }

    def btn2(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Requests',
            'view_mode': 'kanban',
            'res_model': 'approval.request',
            'domain': ['&', ('approval_type_id', '=', self.id), ('state', '=', 'rejected')],
            'create': True
        }

    def btn3(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Requests',
            'view_mode': 'kanban',
            'res_model': 'approval.request',
            'domain': ['&',('approval_type_id', '=', self.id),('state','=','submitted')],
            'create': True
        }