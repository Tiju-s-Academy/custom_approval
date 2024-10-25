from odoo import models, fields


class HoldRequestWizard(models.TransientModel):
    _name = 'hold.request.wizard'

    hold_date = fields.Date(string='Hold Date', required=True)
    approval_request_id = fields.Many2one('approval.request', string='Approval Request', readonly=True)

    def action_submit_hold_date(self):
        # Ensure that we have an approval_request_id to write to
        if self.approval_request_id:
            # Write the hold_date to the Approval Request's hold_date field
            self.approval_request_id.write({
                'hold_date': self.hold_date,
                'state': 'on_hold'
            })



