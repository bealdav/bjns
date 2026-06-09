from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    quick_payment_method_ids = fields.Many2many(
        comodel_name="account.payment.method.line", relation="quick_payment_method_rel"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    quick_payment_method_ids = fields.Many2many(
        comodel_name="account.payment.method.line",
        related="company_id.quick_payment_method_ids",
        domain=[("payment_type", "=", "inbound")],
        readonly=False,
    )
