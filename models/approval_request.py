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
                              ('rejected', 'Rejected')], default='draft', string='Status',
                             tracking=True)
    description = fields.Text(string='Description')
    approver_ids = fields.One2many('approval.type.approver', related='approval_type_id.approver_ids',
                                   string='Approvers', readonly=True)

    approved_by_ids = fields.Many2many('res.users', string='Approved By', readonly=True)
    approval_count = fields.Integer(string="Approval Count", default=0, store=True)
    approval_date = fields.Datetime(string='Approval Date', readonly=True,tracking=True)

    sequence = fields.Integer(compute='_compute_sequence', store=True)

    @api.depends('state')
    def _compute_sequence(self):
        for record in self:
            if record.state == 'draft':
                record.sequence = 1
            elif record.state == 'submitted':
                record.sequence = 2
            elif record.state == 'approved':
                record.sequence = 3
            elif record.state == 'rejected':
                record.sequence = 4
            elif record.state == 'canceled':
                record.sequence = 5

    def action_submit(self):
        """ when submitted  approvel request it will change the state into submitted"""

        self.state = 'submitted'

    def action_approve(self):
        """ Function to approve the approval request, based on weightage.
            If the approver with the maximum weightage approves, the request is automatically approved.
        """
        # Find the maximum weightage among the approvers
        max_weightage = max(self.approver_ids.mapped('weightage')) if self.approver_ids else 0
        current_user = self.env.user

        # Check if the current user is an approver
        if current_user in self.approver_ids.mapped('approver_id'):
            # Check if the current user has already approved
            if current_user not in self.approved_by_ids:
                # Add the current user to the approved list
                self.approved_by_ids = [(4, current_user.id)]

                self.approval_count += 1  # Increment the count

                # Write the updated count to the database
                self.write({'approval_count': self.approval_count})

                # Get the current user's weightage
                current_approver_weightage = self.approver_ids.filtered(lambda approver: approver.approver_id == current_user).weightage

                # If the current user has the maximum weightage, automatically approve
                if current_approver_weightage == max_weightage:
                    self.state = 'approved'
                    self.write({'state': self.state, 'approval_date': fields.Datetime.now()})
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': 'Approved by highest weightage',
                            'type': 'rainbow_man',
                        }
                    }
                # If approval count matches the number of approvers, approve
                elif self.approval_count >= len(self.approver_ids):
                    self.state = 'approved'
                    self.write({'state': self.state, 'approval_date': fields.Datetime.now()})
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': 'Approved',
                            'type': 'rainbow_man',
                        }
                    }
            else:
                raise UserError(_('You have already approved this request.'))
        else:
            raise UserError(_('You are not an approver.'))

    def action_reject(self):
        """ Change the state to 'rejected' only if the current user has the highest weightage,
            or if all higher-priority approvers have already approved/rejected. """

        current_user = self.env.user
        approvers = self.approver_ids.sorted(lambda a: -a.weightage)  # Sort approvers by weightage in descending order
        highest_weightage_approver = approvers[0] if approvers else None  # The highest priority approver

        if current_user in self.approver_ids.mapped('approver_id'):
            # Find the current user's approval entry
            current_approver = self.approver_ids.filtered(lambda a: a.approver_id == current_user)

            # Ensure that the current user is an approver
            if current_approver:
                # Get the highest-priority approver who hasn't acted yet
                for approver in approvers:
                    if approver.is_approved is False and approver.approver_id != current_user:
                        # A higher-priority approver still hasn't approved/rejected, so no rejection yet
                        raise UserError(_('You cannot reject this request until higher priority approvers have acted.'))

                # If the current user is the highest-priority approver or no higher-priority approver is left, reject
                self.state = 'rejected'
                self.write({'state': self.state})
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Rejected',
                        'type': 'rainbow_man',
                    }
                }
            else:
                raise UserError(_('You are not an approver.'))
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
        """ state changes into draft"""
        self.state = 'draft'
        self.write({'state': self.state})

