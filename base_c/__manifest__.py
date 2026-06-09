{
    "name": "Base custom",
    "summary": "Base custom: minimal with mainly depends on Odoo core",
    "category": "Misc",
    "author": "Akretion",
    "license": "AGPL-3",
    "version": "18.0.1.0.2",
    "depends": [
        "contacts",
        "cost_from_supplierinfo",
        "l10n_fr",  # better to primarly load this instead of 'account'
        "maintenance",
        "product_second_category",
        "purchase",
        "sale_management",
        "sale_stock",
    ],
    "data": [
        "security/group.xml",
        "data/misc.xml",
        "views/partner.xml",
        "views/category.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
}
