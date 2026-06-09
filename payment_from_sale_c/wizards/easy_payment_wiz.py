from odoo import _, api, models, fields
from odoo.exceptions import UserError


class EasyPaymentAbstract(models.AbstractModel):
    _name = "easy.payment.abstract"
    _description = "Easy payment mixin"
    _rec_name = "payment_method_line_id"

    payment_method_line_id = fields.Many2one(
        comodel_name="account.payment.method.line", string="Payment"
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


class EasyPaymentWiz(models.TransientModel):
    _name = "easy.payment.wiz"
    _inherit = "easy.payment.abstract"
    _description = "Easy payment from sale"

    company_id = fields.Many2one(comodel_name="res.company", required=True)
    amount = fields.Float(readonly=True)
    due = fields.Float(compute="_compute_due", readonly=True)
    currency_id = fields.Many2one(comodel_name="res.currency")
    line_ids = fields.One2many(
        comodel_name="easy.payment.line.wiz", inverse_name="easy_payment_id"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sale = self.env["sale.order"].browse(self._context.get("active_id"))
        res["company_id"] = sale.company_id.id
        res["currency_id"] = sale.currency_id.id
        res["amount"] = sale.amount_total
        return res

    @api.depends("line_ids", "line_ids.amount", "amount")
    def _compute_due(self):
        for rec in self:
            rec.due = rec.amount - sum(rec.line_ids.mapped("amount"))

    def invoice_and_pay(self):
        self.ensure_one()
        if not self.payment_method_line_id and self.line_ids and self.due:
            # Coming from view, you can't dive here: kept for api case
            raise UserError(
                f"La somme des paiements devrait être de '{self.due}' au "
                f"lieu de '{sum(self.line_ids.mapped('amount'))}'"
            )
        if not self.payment_method_line_id and not self.line_ids:
            # Coming from view, you can't dive here: kept for api case
            raise UserError("Veuillez sélectionner un paiement.")
        sale = self.env["sale.order"].browse(self._context.get("active_id"))
        so_context = {
            "active_model": "sale.order",
            "active_ids": [sale.id],
            "active_id": sale.id,
        }
        # invoice creation
        payment_params = {
            "advance_payment_method": "delivered",
            "amount": self.amount,
        }
        downpayment = (
            self.env["sale.advance.payment.inv"]
            .with_context(so_context)
            .create(payment_params)
        )
        res = downpayment.sudo().create_invoices()
        invoice = self.env["account.move"].browse(res.get("res_id"))
        invoice.sudo().action_post()
        if invoice.amount_total != self.amount:
            raise UserError(
                f"Montant facturé = {invoice.amount_total} <> "
                + f"montant vendu {self.amount} !\n"
                + "Faites l'opération manuellement et idenitifiez la cause !"
            )
        # payment management
        if self.payment_method_line_id:
            pay_vals_list = [
                {
                    "journal_id": self.payment_method_line_id.journal_id.id,
                    "payment_method_line_id": self.payment_method_line_id.id,
                    "payment_date": self.payment_date,
                    "group_payment": True,
                    "amount": self.amount,
                    "currency_id": sale.currency_id.id,
                }
            ]
        else:
            vals = {
                "payment_date": self.payment_date,
                "group_payment": True,
                "currency_id": sale.currency_id.id,
            }
            pay_vals_list = []
            for pay in self.line_ids:
                payment_vals = {
                    "journal_id": pay.payment_method_line_id.journal_id.id,
                    "payment_method_line_id": pay.payment_method_line_id.id,
                    "amount": pay.amount,
                }
                payment_vals.update(vals)
                pay_vals_list.append(payment_vals)
        payments = self.env["account.payment"]
        for pay in pay_vals_list:
            payments |= (
                self.env["account.payment.register"]
                .with_context(active_model="account.move", active_ids=[invoice.id])
                .sudo()
                .create(pay)
                ._create_payments()
            )
        sale.message_post(
            body=_(
                "Paiements: "
                + ", ".join(
                    [f"{x.payment_method_line_id.name}: {x.amount}" for x in payments]
                )
            )
        )
        # action to view invoice
        return res
