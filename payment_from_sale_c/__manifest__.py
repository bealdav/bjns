{
    "name": "Payment from Sale",
    "summary": "Custom quick payment from sale",
    "version": "18.0.1.0.0",
    "author": "Akretion",
    "license": "AGPL-3",
    "depends": [
        "sale_stock",
        "l10n_fr_account",
        "sale_deliver_service_as_goods",
    ],
    "exclude": [],
    "data": [
        "wizards/easy_payment_wiz.xml",
        "views/settings.xml",
        "views/sale.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
