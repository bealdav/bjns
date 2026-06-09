from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    easy_payable = fields.Boolean(
        compute="_compute_easy_payable", store=True, help="Authorize quick payment"
    )

    @api.depends(
        "order_line.qty_delivered", "order_line.product_uom_qty", "invoice_status"
    )
    def _compute_easy_payable(self):
        for rec in self:
            easy_payable = False
            if rec.state == "sale" and rec.invoice_status == "to invoice":
                to_ship = [
                    x for x in rec.order_line if x.product_uom_qty != x.qty_delivered
                ]
                if not to_ship:
                    easy_payable = True
            elif rec.invoice_status == "invoiced":
                easy_payable = False
            rec.easy_payable = easy_payable
