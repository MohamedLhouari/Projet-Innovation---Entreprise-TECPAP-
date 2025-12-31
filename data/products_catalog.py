"""
Catalogue des produits TECPAP
"""

# Catalogue des produits disponibles
PRODUCTS_CATALOG = [
    {
        "code": "P001",
        "name": "Fond plat",
        "type": "Sac papier",
        "grammage": 80,
        "vitesse_recommandee": 450,
        "vitesse_min": 350,
        "vitesse_max": 550
    },
    {
        "code": "P002",
        "name": "Fond carré sans poignées",
        "type": "Sac papier",
        "grammage": 90,
        "vitesse_recommandee": 420,
        "vitesse_min": 320,
        "vitesse_max": 520
    },
    {
        "code": "P003",
        "name": "Fond carré avec poignées plates",
        "type": "Sac papier",
        "grammage": 100,
        "vitesse_recommandee": 380,
        "vitesse_min": 280,
        "vitesse_max": 480
    },
    {
        "code": "P004",
        "name": "Fond carré avec poignées torsadées",
        "type": "Sac papier",
        "grammage": 100,
        "vitesse_recommandee": 360,
        "vitesse_min": 260,
        "vitesse_max": 460
    }
]

def get_all_products():
    """Retourne tous les produits du catalogue"""
    return PRODUCTS_CATALOG

def get_product_by_code(product_code):
    """Retourne un produit spécifique par son code"""
    for product in PRODUCTS_CATALOG:
        if product["code"] == product_code:
            return product
    return None

def get_product_types():
    """Retourne la liste des types de produits disponibles"""
    return list(set([p["type"] for p in PRODUCTS_CATALOG]))
