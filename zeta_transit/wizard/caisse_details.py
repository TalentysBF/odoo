from odoo import api, fields, models
from odoo.exceptions import UserError


class ZetaTransCaisseDetailsWizard(models.TransientModel):
    _name = 'zeta.trans.caisse.details.wizard'
    _description = 'Open Sale Details Report'

    def _default_start_date(self):
        """ Find the earliest start_date of the latests sessions """
        self.env.cr.execute("""
            SELECT
            max(create_date) as start
            FROM zeta_trans_caisse
            WHERE create_date > (NOW() - INTERVAL '2 DAYS')
        """)
        latest_start_dates = [res['start'] for res in self.env.cr.dictfetchall()]
        # earliest of the latest sessions
        return latest_start_dates and min(latest_start_dates) or fields.Datetime.now()

    start_date = fields.Datetime(required=True, default=_default_start_date)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report(self):
        data = {'date_start': self.start_date, 'date_stop': self.end_date}
        return self.env['report'].get_action(
            [], 'zeta_transit.report_zeta_caisse_details', data=data)
