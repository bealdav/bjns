from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _search_display_name(self, operator, value):
        domain = super()._search_display_name(operator, value)
        # we want to be able to search by supplier code for the product from any place
        # (but mainly sale order). So, systematically search on seller_ids.product_code
        # unless we got partner in context (in that case native Odoo already search
        # for the product_code in combination with the supplier, this should be enough
        partner_id = self.env.context.get("partner_id", False)
        partner = self.env["res.partner"].browse(partner_id)
        # we try to keep native behavior as much as we can, only search for all supplier
        # code in the given partner is not a supplier, else we only search the code
        # for this supplier (native)
        if not partner.supplier_rank:
            domains = [domain]
            is_positive = operator not in expression.NEGATIVE_TERM_OPERATORS
            combine = expression.OR if is_positive else expression.AND
            domains.append(
                [("product_tmpl_id.seller_ids.product_code", operator, value)]
            )
            domain = combine(domains)
        return domain

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super().name_search(name=name, args=args, operator=operator, limit=limit)
        # maybe we should do it even if a res exists in case we do not have any
        # self.env.context.get("partner_id")
        if not res:
            domain = args or []
            # still no results, partner in context: search on supplier info as last hope to find something
            supplier_domain = [
                ('product_code', operator, name),
            ]
            match_domain = [('product_tmpl_id.seller_ids', 'any', supplier_domain)]
            products = self.search_fetch(expression.AND([domain, match_domain]), ['display_name'], limit=limit)
            res = [(product.id, product.display_name) for product in products.sudo()] 
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_second_id = fields.Many2one(comodel_name="product.category", string="Famille")
