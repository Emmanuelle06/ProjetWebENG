import sqlite3
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('BD/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def add_repas(repas):
    db = get_db()
    try:
        db.execute(
                "INSERT INTO repas (nom, prix, description, disponibilite, image, id_vendeur)" \
                "VALUES (:nom, :prix, :description, :disponibilite, :image, :id_vendeur)",
                repas
            )
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False

def add_commande(commande):
    db = get_db()
    try:
        curseur = db.execute(
            "INSERT INTO commande (id_acheteur, statut, cout_total)" \
            "VALUES (:id_acheteur, :statut, :cout_total)",
            commande
        )
        db.commit()
        return curseur.lastrowid
    except Exception as e:
        print(e)
        return False

def commande_repas(repas):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO commande_repas (id_commande, id_repas, quantite, prix_unitaire)" \
            "VALUES (:id_commande, :id_repas, :quantite, :prix_unitaire)",
            repas
        )
        db.commit()
        return True
    except Exception as e:
        print (e)
        return False

def get_repas(id):
    db = get_db()
    try:
        repas = db.execute(
            "Select * from repas where id_repas = ?",
        (id,)
        ).fetchone()
        return repas
    except Exception as e:
        print(e)
        return False

def get_restaurant(id_repas):
    db = get_db()
    try:
        resto = db.execute(
            "Select v.nom_restaurant from repas r " \
            "JOIN vendeur v ON r.id_vendeur = v.id where r.id_repas = ?",
        (id_repas,)
        ).fetchone()
        return resto
    except Exception as e:
            print(e)
            return False

#fonction pour obtenir les repas dun client, supprimer et rendre son repas indisponible

def obtenir_mes_repas(id_vendeur):
    base_de_donnees = get_db()

    repas = base_de_donnees.execute(
        """
        SELECT id_repas, nom, prix, description, disponibilite,image
        FROM repas
        WHERE id_vendeur = ?
        ORDER BY id_repas DESC
        """,
        (id_vendeur,)
    ).fetchall()

    return repas


def obtenir_repas(id_repas, id_vendeur):
    base_de_donnees = get_db()

    repas = base_de_donnees.execute(
        """
        SELECT id_repas, nom, prix, description, disponibilite, image
        FROM repas
        WHERE id_repas = ? AND id_vendeur = ?
        """,
        (id_repas, id_vendeur)
    ).fetchone()

    return repas


def modifier_disponibilite(id_repas, id_vendeur, disponibilite):
    base_de_donnees = get_db()

    curseur = base_de_donnees.execute(
        """
        UPDATE repas
        SET disponibilite = ?
        WHERE id_repas = ? AND id_vendeur = ?
        """,
        (disponibilite, id_repas, id_vendeur)
    )

    base_de_donnees.commit()

    return curseur.rowcount > 0


def supprimer_repas(id_repas, id_vendeur):
    base_de_donnees = get_db()

    curseur = base_de_donnees.execute(
        """
        DELETE FROM repas
        WHERE id_repas = ? AND id_vendeur = ?
        """,
        (id_repas, id_vendeur)
    )

    base_de_donnees.commit()

    return curseur.rowcount > 0


def get_acheteur(id_acheteur):
    db = get_db()
    try:
        acheteur = db.execute(
            "Select credit from acheteur where id = ?",
            (id_acheteur,)
            ).fetchone()
        return acheteur
    except Exception as e:
            print(e)
            return False

def modif_credit(id_acheteur, nouv_credit):
    db = get_db()
    try:
        db.execute(
            "update acheteur SET credit = ? where id = ?",
            (nouv_credit, id_acheteur)
        )
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False


def modifier_repas(repas):
    """Modifie un repas du vendeur. Si image vaut None, on garde l'ancienne image."""
    db = get_db()
    try:
        curseur = db.execute("""
            UPDATE repas
            SET nom = :nom, prix = :prix, description = :description,
                disponibilite = :disponibilite, image = COALESCE(:image, image)
            WHERE id_repas = :id_repas AND id_vendeur = :id_vendeur""",
            repas)
        db.commit()
        return curseur.rowcount > 0
    except Exception as e:
        print(e)
        return False


def obtenir_repas_disponibles(prix_min, prix_max):
    """Retourne les repas disponibles dont le prix est entre prix_min et prix_max"""
    return get_db().execute("""
        SELECT repas.id_repas, repas.nom, repas.prix, vendeur.nom_restaurant
        FROM repas
        LEFT JOIN vendeur ON repas.id_vendeur = vendeur.id
        WHERE repas.disponibilite IN ('on', 1)
        AND repas.prix >= :prix_min
        AND repas.prix <= :prix_max""",
        {"prix_min": prix_min, "prix_max": prix_max}).fetchall()


def obtenir_repas_par_id(id_repas):
    """Retourne un repas disponible avec son restaurant (ou None s'il n'existe pas)"""
    return get_db().execute("""
        SELECT repas.id_repas, repas.nom, repas.prix,repas.image ,repas.description, vendeur.nom_restaurant
        FROM repas
        LEFT JOIN vendeur ON repas.id_vendeur = vendeur.id
        WHERE repas.id_repas = :id_repas
        AND repas.disponibilite IN ('on', 1)""",
        {"id_repas": id_repas}).fetchone()

#fonction pour avoir les commandes dun acheteur

def obtenir_commandes_acheteur(id_acheteur):
    """ Retoune les commandes d'un acheteur"""
    db = get_db()

    try:
        curseur = db.execute(
            """
            SELECT
                commande.id_commande,commande.statut, commande.cout_total
                ,repas.nom,repas.id_repas,commande_repas.quantite,commande_repas.prix_unitaire
            FROM commande
            LEFT JOIN commande_repas
                ON commande.id_commande = commande_repas.id_commande
            LEFT JOIN repas
                ON commande_repas.id_repas = repas.id_repas
            WHERE commande.id_acheteur = ?
            ORDER BY commande.id_commande DESC
            """,
            (id_acheteur,)
        )

        lignes = curseur.fetchall()
        commandes = []

        for ligne in lignes:
            commande_trouvee = None

            for commande in commandes:
                if commande["id_commande"] == ligne["id_commande"]:
                    commande_trouvee = commande
                    break

            if commande_trouvee is None:
                commande_trouvee = {
                    "id_commande": ligne["id_commande"],
                    "statut": ligne["statut"],
                    "cout_total": ligne["cout_total"],
                    "repas": []
                }
                commandes.append(commande_trouvee)

            if ligne["nom"] is not None:
                commande_trouvee["repas"].append({
                    "id_repas": ligne["id_repas"],
                    "nom": ligne["nom"],
                    "prix": ligne["prix_unitaire"],
                    "quantite": ligne["quantite"]
                })

        return commandes

    except Exception as e:
        print(e)
        return []

