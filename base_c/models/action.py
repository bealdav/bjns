from odoo import api, models


class IrActionsAct_windowView(models.Model):
    _inherit = "ir.actions.act_window.view"

    @api.model
    def _contact_default_view_type(self):
        self.search(
            [
                ("view_mode", "=", "kanban"),
                ("act_window_id", "=", self.env.ref("contacts.action_contacts").id),
            ]
        ).sequence = 2
