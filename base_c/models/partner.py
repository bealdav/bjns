from odoo import fields, models
import logging

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    lang = fields.Selection(default="fr_FR")
    invoice_sending_method = fields.Selection(default="email")

    def _country_df_sage100_replacement(self):
        # Used by db_process module that is not in dependency of this module
        return {
            "ALLEMAGNE": "Allemagne",
        }
