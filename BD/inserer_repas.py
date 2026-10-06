import sqlite3
from pathlib import Path

DOSSIER = Path("static/images/image_repas")

# (nom, prix, description, fichier, restaurant)
REPAS = [
    ("Gâteau au chocolat", 12, "Gâteau moelleux au chocolat noir",          "gateau.jpg",       "Chez Marco"),
    ("Boeuf fumé",         17, "Boeuf fumé maison, tranché finement",       "boeuf_fume.webp",  "Chez Marco"),
    ("Hamburger",          16, "Boeuf grillé, fromage, laitue et tomate",   "hamburger.webp",   "Chez Marco"),
    ("Boeuf saignant",      6, "Pièce de boeuf grillée, cuisson saignante", "steak.webp",       "Chez Marco"),
    ("Poisson braisé",     22, "Poisson entier braisé aux herbes",          "poisson.webp",     "Sushi Zen"),
    ("Beignets",           15, "Beignets dorés saupoudrés de sucre",        "beignets.webp",    "Sushi Zen"),
    ("Poutine",            14, "Frites, fromage en grains et sauce brune",  "poutine.webp",     "Sushi Zen"),
    ("Oeuf au plat",       14, "Deux oeufs au plat, pain grillé",           "oeuf.webp",        "Burger House"),
    ("Pizza",              13, "Sauce tomate, mozzarella et basilic",       "pizza.webp",       "Burger House"),
]

connexion = sqlite3.connect("BD/eatfast.sqlite")
for nom, prix, description, fichier, restaurant in REPAS:
    connexion.execute(
        """INSERT INTO repas (nom, prix, description, disponibilite, image, id_vendeur)
           VALUES (?, ?, ?, 'on', ?, (SELECT id FROM vendeur WHERE nom_restaurant = ?))""",
        (nom, prix, description, (DOSSIER / fichier).read_bytes(), restaurant)
    )
connexion.commit()
connexion.close()