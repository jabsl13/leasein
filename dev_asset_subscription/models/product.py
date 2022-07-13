# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class product_template(models.Model):
    _inherit = "product.template"

    @api.onchange('type')
    def _onchange_product_type(self):
        return {}

    @api.onchange('recurring_invoice')
    def _onchange_recurring_invoice(self):
        return {}

    @api.constrains('recurring_invoice', 'type')
    def _check_subscription_product(self):
        return {}
