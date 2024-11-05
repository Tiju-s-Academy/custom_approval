from odoo import models, fields,_,api
from odoo.exceptions import UserError
import logging


class ApprovalRequest(models.Model):
    """ module is used for request approvals"""
    _name = 'approval.request'
    _description = 'Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Approval Subject', required=True, tracking=True)
    approval_type_id = fields.Many2one('approvals.types', string='Approval Type', required=True)
    request_owner_id = fields.Many2one('res.users', string='Request Owner', default=lambda self: self.env.user,
                                       readonly=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today, readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'),('on_hold','On Hold'), ('approved', 'Approved'),
                              ('rejected', 'Rejected')], default='draft', string='Status',
                             tracking=True)
    description = fields.Text(string='Description')
    approver_ids = fields.One2many('approval.type.approver', related='approval_type_id.approver_ids',
                                   string='Approvers', readonly=True)

    approved_by_ids = fields.Many2many('res.users', string='Approved By', readonly=True,tracking=True)
    approval_count = fields.Integer(string="Approval Count", default=0, store=True)
    approval_date = fields.Datetime(string='Approval Date', readonly=True,tracking=True)

    sequence = fields.Integer(compute='_compute_sequence', store=True)
    hold_date = fields.Date(string='Hold Date',tracking=True)


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

    @api.model
    def create(self, vals):
        """ Override the create method to send activities to approvers. """
        record = super(ApprovalRequest, self).create(vals)
        print("hello")


        # Send an activity to all approvers
        approvers = record.approver_ids.mapped('approver_id')
        if approvers:
            for approver in approvers:
                record.activity_schedule(
                    activity_type_id=self.env.ref('custom_approval.mail_activity_data_todo').id,
                    user_id=approver.id,
                )
        return record

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
                self.approval_date = fields.Datetime.now()
                self.approval_count += 1  # Increment the count

                # Write the updated count to the database
                self.write({'approval_count': self.approval_count})

                # Get the current user's weightage
                current_approver_weightage = self.approver_ids.filtered(lambda approver: approver.approver_id == current_user).weightage

                # If the current user has the maximum weightage, automatically approve
                if current_approver_weightage == max_weightage:
                    self.state = 'approved'
                    self.write({'state': self.state, 'approval_date': fields.Datetime.now()})
                    super().activity_unlink(['mail.mail_activity_data_todo'])
                    print(super().activity_unlink(['mail.mail_activity_data_todo']))
                    activity_ids = self.activity_ids
                    if activity_ids:
                        activity_ids.unlink()
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

        """ Reject the approval request if the current user is an approver.
                If any higher-priority approver has already rejected, move to rejected state.
            """
        current_user = self.env.user
        # Check if the current user is an approver
        if current_user in self.approver_ids.mapped('approver_id'):

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

    def action_withdraw(self):
        """ Withdraw approval from the approval request.
            If the user is an approver, remove them from the approved list and reset the state to 'submitted'.
        """
        current_user = self.env.user

        # Check if the current user is an approver
        if current_user in self.approver_ids.mapped('approver_id'):
            # Check if the current user has already approved
            if current_user in self.approved_by_ids:
                # Remove the current user from the approved list
                self.approved_by_ids = [(3, current_user.id)]  # 3 means to unlink

                # Decrement the approval count
                self.approval_count -= 1
                self.write({'approval_count': self.approval_count})

                # Set the state to 'submitted'
                self.state = 'submitted'
                self.write({'state': self.state})

                # Save the changes
                return True  # Optionally return True to indicate success
            else:
                raise UserError(_('You have not approved this request yet.'))
        else:
            raise UserError(_('You are not an approver.'))

    def action_cancel(self):
        """ state changes into draft"""
        self.state = 'draft'
        self.write({'state': self.state})

    def action_on_hold(self):
        current_user = self.env.user
        # Check if the current user is an approver
        if current_user in self.approver_ids.mapped('approver_id'):
            return {
                'type': 'ir.actions.act_window',
                'name': _('Hold Date'),
                'res_model': 'hold.request.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_approval_request_id': self.id},
            }
        else:
            raise UserError(_('You are not an approver.'))

    def action_ask_query(self):
        followers = self.message_follower_ids.mapped('partner_id.user_ids')
        print("helloo")
        print(followers)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ask Query'),
            'res_model': 'ask.query.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'default_follower_ids': [(6, 0, followers.ids)],
                'follower_ids': followers.ids,  # Pass IDs for domain
                'default_record_id': self.id
            }
        }


