from odoo import models, fields,api,_
from odoo.exceptions import UserError


class AskQueryWizard(models.TransientModel):
    _name = 'ask.query.wizard'

    follower_ids = fields.Many2many('res.users', string='Followers')
    query_text = fields.Text(string='Query')
    record_id = fields.Many2one('approval.request', string='Related Record')



    def action_submit_query(self):
        if not self.record_id:
            raise UserError(_("The main record does not exist."))

            # Ensure the record exists
        record = self.record_id
        if not record.exists():
            raise UserError(_("The related record is not found."))

        # Loop through each follower and schedule the activity on the main record
        for follower in self.follower_ids:
            record.activity_schedule(
                activity_type_id=self.env.ref('custom_approval.mail_activity_data_todo').id,
                user_id=follower.id,
                summary=self.query_text,  # Use the query text as the summary
                note=self.query_text  # You can use this for any additional note if needed
            )

        return {'type': 'ir.actions.act_window_close'}









