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
                "INSERT INTO REPAS (nom, prix, description, disponibilite, image, id_vendeur)" \
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
        db.execute(
            "INSERT INTO commande (id_acheteur, statut)" \
            "VALUES (:id_acheteur, :statut)"
        )
    except Exception as e:
        print(e)
        return False

def commande_repas(repas):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO commande_repas (id_commande, id_repas, quantite)" \
            "VALUES ()"
        )
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