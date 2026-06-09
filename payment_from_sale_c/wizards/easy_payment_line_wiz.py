from odoo import fields, api, models


class EasyPaymentLineWiz(models.TransientModel):
    _name = "easy.payment.line.wiz"
    _inherit = "easy.payment.abstract"
    _description = "Easy payment line from sale"

    easy_payment_id = fields.Many2one(comodel_name="easy.payment.wiz", required=True)
    amount = fields.Float(compute="_compute_amount", store=True, readonly=False)
    company_id = fields.Many2one(
        comodel_name="res.company", related="easy_payment_id.company_id", readonly=True
    )
    payment_domain = fields.Binary(
        compute="_compute_payment_domain", help="Dynamic domain used for any field"
    )
    payment_date = fields.Date(string="Date", default=fields.Date.today())

    @api.depends("company_id")
    def _compute_payment_domain(self):
        for rec in self:
            rec.payment_domain = [
                ("id", "in", self.company_id.quick_payment_method_ids.ids)
            ]

    @api.depends("easy_payment_id")
    def _compute_amount(self):
        ctx = self._context
        sale = self.env["sale.order"].browse(ctx.get("active_ids")[0])
        for rec in self:
            rec.amount = sale.amount_total - sum(
                rec.easy_payment_id.line_ids.mapped("amount")
            )
