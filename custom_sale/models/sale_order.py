from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    notes_logistiques = fields.Html(
        string='Logistics Notes',
        sanitize=True,
        translate=False,
    )
