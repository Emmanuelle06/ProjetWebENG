import sqlite3

# Hachage SHA512 du mot de passe "1234"
MOT_DE_PASSE = "d404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db"

VENDEURS = [
    {"username": "marco",  "nom_restaurant": "Chez Marco"},
    {"username": "zen",    "nom_restaurant": "Sushi Zen"},
    {"username": "burger", "nom_restaurant": "Burger House"},
]

REPAS = [
    {"nom": "Gâteau au chocolat", "prix": 12, "description": "Gâteau moelleux au chocolat noir",          "fichier": "gateau.jpg",      "restaurant": "Chez Marco"},
    {"nom": "Boeuf fumé",         "prix": 17, "description": "Boeuf fumé maison, tranché finement",       "fichier": "boeuf_fume.webp", "restaurant": "Chez Marco"},
    {"nom": "Hamburger",          "prix": 16, "description": "Boeuf grillé, fromage, laitue et tomate",   "fichier": "hamburger.webp",  "restaurant": "Chez Marco"},
    {"nom": "Boeuf saignant",     "prix": 6,  "description": "Pièce de boeuf grillée, cuisson saignante", "fichier": "steak.webp",      "restaurant": "Chez Marco"},
    {"nom": "Poisson braisé",     "prix": 22, "description": "Poisson entier braisé aux herbes",          "fichier": "poisson.webp",    "restaurant": "Sushi Zen"},
    {"nom": "Beignets",           "prix": 15, "description": "Beignets dorés saupoudrés de sucre",        "fichier": "beignets.webp",   "restaurant": "Sushi Zen"},
    {"nom": "Poutine",            "prix": 14, "description": "Frites, fromage en grains et sauce brune",  "fichier": "poutine.webp",    "restaurant": "Sushi Zen"},
    {"nom": "Oeuf au plat",       "prix": 14, "description": "Deux oeufs au plat, pain grillé",           "fichier": "oeuf.webp",       "restaurant": "Burger House"},
    {"nom": "Pizza",              "prix": 13, "description": "Sauce tomate, mozzarella et basilic",       "fichier": "pizza.webp",      "restaurant": "Burger House"},
]


def inserer_donnees_test(connexion):
    """Insère les vendeurs et repas de test, seulement si aucun repas n'existe."""
    if connexion.execute("SELECT COUNT(*) FROM repas").fetchone()[0] > 0:
        return

    for vendeur in VENDEURS:
        connexion.execute(
            """INSERT OR IGNORE INTO utilisateur (username, mot_de_passe, statut)
               VALUES (:username, :mot_de_passe, :statut)""",
            {
                "username": vendeur["username"],
                "mot_de_passe": MOT_DE_PASSE,
                "statut": "vendeur"
            }
        )

        connexion.execute(
            """INSERT OR IGNORE INTO vendeur (id, telephone, nom_restaurant, adresse_postale, condition)
               VALUES ((SELECT id FROM utilisateur WHERE username = :username),
                       :telephone, :nom_restaurant, :adresse, :condition)""",
            {
                "username": vendeur["username"],
                "telephone": "5141234567",
                "nom_restaurant": vendeur["nom_restaurant"],
                "adresse": "123 rue Test, Montréal",
                "condition": True
            }
        )

    for repas in REPAS:
        with open("static/images/image_repas/" + repas["fichier"], "rb") as fichier:
            contenu_image = fichier.read()

        connexion.execute(
            """INSERT INTO repas (nom, prix, description, disponibilite, image, id_vendeur)
               VALUES (:nom, :prix, :description, :disponibilite, :image,
                       (SELECT id FROM vendeur WHERE nom_restaurant = :restaurant))""",
            {
                "nom": repas["nom"],
                "prix": repas["prix"],
                "description": repas["description"],
                "disponibilite": "on",
                "image": contenu_image,
                "restaurant": repas["restaurant"]
            }
        )

    connexion.commit()


if __name__ == "__main__":
    connexion = sqlite3.connect("BD/eatfast.sqlite")
    inserer_donnees_test(connexion)
    connexion.close()
