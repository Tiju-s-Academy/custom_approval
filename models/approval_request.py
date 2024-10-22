from odoo import models, fields,_,api
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    """ module is used for request approvals"""
    _name = 'approval.request'
    _description = 'Approval Request'
    _inherit = 'mail.thread'

    name = fields.Char(string='Approval Subject', required=True, tracking=True)
    approval_type_id = fields.Many2one('approvals.types', string='Approval Type', required=True)
    request_owner_id = fields.Many2one('res.users', string='Request Owner', default=lambda self: self.env.user,
                                       readonly=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today, readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'),
                              ('canceled', 'Canceled'), ('rejected', 'Rejected')], default='draft', string='Status',
                             tracking=True)
    description = fields.Text(string='Description')
    approver_ids = fields.One2many('approval.type.approver', related='approval_type_id.approver_ids',
                                   string='Approvers', readonly=True)
    approved_by_ids = fields.Many2many('res.users', string='Approved By', readonly=True)
    approval_count = fields.Integer(string="Approval Count", default=0, store=True)

    def action_submit(self):
        """ when submitted  approvel request it will change the state into submitted"""

        self.state = 'submitted'

    def action_approve(self):
        """ function to approve the approval request and check the current user and check the current user as
         approver becuse the approver can only approve the approval request. also it ensure the approvers are approved
          then only move to the approved state"""

        current_user = self.env.user
        if current_user in self.approver_ids.mapped('approver_id'):
            if current_user not in self.approved_by_ids:
                self.approved_by_ids = [(4, current_user.id)]
                self.approval_count += 1  # Increment the count

                # Write the updated count to the database
                self.write({'approval_count': self.approval_count})
                # Check if the approval count matches the number of approvers
                if self.approval_count >= len(self.approver_ids):
                    self.state = 'approved'
            else:
                raise UserError(_('You have already approved this request.'))
        else:
            raise UserError(_('You are not an approver.'))

    def action_reject(self):
        """ change the state into rejected ,can do only the approvers"""

        current_user = self.env.user
        if current_user in self.approver_ids.mapped('approver_id'):
            self.state = 'rejected'
        else:
            raise UserError(_('You are not an approver.'))

    def action_withdraw(self):
        """ function for withdraw the approval request"""
        for request in self:
            if request.approval_count > 0:
                request.approval_count -= 1  # Decrement the count
            request.state = 'submitted'  # Change the state back to submitted
            request.approved_by_ids = [(3, request.env.user.id)]

    def action_cancel(self):
        """ state changes into canceled"""
        self.state = 'canceled'
