from odoo import models, fields


class HoldRequestWizard(models.TransientModel):
    _name = 'hold.request.wizard'

    hold_date = fields.Date(string='Hold Date', required=True)



