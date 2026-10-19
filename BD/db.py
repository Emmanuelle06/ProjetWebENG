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
