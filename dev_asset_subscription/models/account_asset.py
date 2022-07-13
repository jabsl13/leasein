# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    categ_id = fields.Many2one('product.category', string='Categoría de Producto')
    warehouse_id = fields.Many2one('stock.warehouse', string='Almacen')
    picking_type_id = fields.Many2one('stock.picking.type', 'Recepcionar en',
                                      required=True,
                                      domain="[('warehouse_id', '=', warehouse_id)]",
                                      help="This will determine operation type of incoming shipment")
    picking_id = fields.Many2one('stock.picking', string='Ingreso al almacén')
    product_id = fields.Many2one('product.product', string='Producto')

    def validate(self):
        super(AccountAsset, self).validate()
        # Registramos el producto
        product = self.env['product.product'].create({
            'name': self.name,
            'detailed_type': 'product',
            'categ_id': self.categ_id.id,
            'standard_price': self.original_value
        })
        self.product_id = product.id
        picking = self._create_picking()
        self.picking_id = picking.id

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        asset = self
        order = asset.with_company(asset.company_id)
        res = order._prepare_picking()
        picking = StockPicking.with_user(SUPERUSER_ID).create(res)

        moves = order._create_stock_moves(picking)
        moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
        seq = 0
        for move in sorted(moves, key=lambda move: move.date):
            seq += 5
            move.sequence = seq
        moves._action_assign()
        picking.message_post_with_view('mail.message_origin_link',
                                       values={'self': picking, 'origin': order},
                                       subtype_id=self.env.ref('mail.mt_note').id)
        return picking

    def _prepare_picking(self):
        return {
            'picking_type_id': self.picking_type_id.id,
            'date': self.acquisition_date,
            'origin': self.name,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'location_id': self.product_id.property_stock_inventory.id,
            'company_id': self.company_id.id,
        }

    def _create_stock_moves(self, picking):
        values = self._prepare_stock_moves(picking)
        return self.env['stock.move'].create(values)

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        price_unit = self.original_value
        vals = {
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': self.acquisition_date,
            'date_deadline': self.acquisition_date,
            'location_id': self.product_id.property_stock_inventory.id,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'picking_id': picking.id,
            'state': 'draft',
            'company_id': self.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.picking_type_id.id,
            'origin': self.name,
            'warehouse_id': self.picking_type_id.warehouse_id.id,
            'product_uom_qty': 1,
            'product_uom': self.product_id.uom_id.id,
        }
        return vals
