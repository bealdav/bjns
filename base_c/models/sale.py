from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _find_mail_template(self):
        """Get the appropriate mail template for the current sales order based on its state."""
        res = super()._find_mail_template()
        if self.state in ("draft", "sent"):
            return self.env.ref(
                "snjb.email_template_edi_sale_snjb", raise_if_not_found=False
            )
        return res
