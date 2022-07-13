# -*- coding: utf-8 -*-
{
    'name': "Crear Activos y Producto x subscripcion",

    'summary': """
        Mejoras requeridas para activo fijos y subscripciones:
        """,
    "description": """
        Modulo de activos fijos:
        -	Crear dato maestro de producto en inventarios al confirmar un activo fijo.
        
        Modulo subscripciones:
        -	Productos almacenables puedan usarse en subscripciones.
    """,

    'author': "sapex.miguel@gmail.com",
    'category': "DEV",
    'version': '15.0.0.1',
    'depends': ['account_asset', 'sale_subscription', 'stock', 'product'],
    'data': [
        'views/account_asset_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
}
