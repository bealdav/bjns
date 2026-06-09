from odoo import fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Used to display ui_ship_all_products
    available_case = fields.Boolean(compute="_compute_available_case")

    def _compute_available_case(self):
        for rec in self:
            pick = rec.picking_ids and rec.picking_ids[0]
            if rec.state == "sale" and (
                not pick
                or (
                    len(pick) == 1
                    and pick.state != "done"
                    and pick.products_availability_state == "available"
                )
            ):
                rec.available_case = True
            else:
                rec.available_case = False

    def ui_ship_all_products_c(self):
        for rec in self:
            # TODO check combo
            if rec.state in ("draft", "sent"):
                rec.action_confirm()
            if not rec.available_case:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Produits à livrer",
                        "type": "warning",
                        "message": """Les conditions ne sont pas réunies pour livrer
                            les produits automatiquement.\nVous devez effectuer les 
                            opérations manuellement.""",
                        "sticky": True,
                        "next": {"type": "ir.actions.client", "tag": "soft_reload"},
                    },
                }
            pick = rec.picking_ids and rec.picking_ids[0]
            if pick:
                if pick.state == "waiting":
                    pick.action_assign()
                try:
                    pick.with_context(skip_sms=True).button_validate()
                except Exception as err:
                    raise UserError(err) from err
                if pick.state != "done":
                    raise UserError("Problème sur le transfert")
            for line in rec.order_line.filtered(
                lambda s: s.product_id.type == "service"
            ):
                line.qty_delivered = line.product_uom_qty
