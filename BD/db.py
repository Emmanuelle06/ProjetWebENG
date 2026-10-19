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
            "INSERT INTO commande_repas (id_commande, id_repas, quantite)" \
            "VALUES (:id_commande, :id_repas, :quantite)",
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
