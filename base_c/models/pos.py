from odoo import models
from odoo.tools import SQL


class PosConfig(models.Model):
    _inherit = "pos.config"

    def get_limited_partners_loading(self):
        "Add customers according to customer_rank field"
        res = super().get_limited_partners_loading()
        partner_with_rank = self.env.execute_query(
            SQL(
                """
            SELECT id FROM res_partner AS p
            WHERE customer_rank > 0 and parent_id is NULL
        """
            )
        )
        res.extend([partner for partner in partner_with_rank])
        return res
