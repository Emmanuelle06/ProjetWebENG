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
            "INSERT INTO repas (nom, prix, description, disponibilite, image, id_vendeur)"
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
            "INSERT INTO commande (id_acheteur, statut, cout_total)"
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
            "INSERT INTO commande_repas (id_commande, id_repas, quantite, prix_unitaire)"
            "VALUES (:id_commande, :id_repas, :quantite, :prix_unitaire)",
            repas
        )
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False


def add_commande_vendeur(id_commande, id_vendeur):
    """ Fonction qui enregistre le restaurant associé à une commande"""
    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO commande_vendeur (id_commande, id_vendeur, statut)
            VALUES (?, ?, 'attente')
            """,
            (id_commande, id_vendeur)
        )
        db.commit()
        return True
    except Exception as e:
        print(e)
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
            "Select v.nom_restaurant from repas r "
            "JOIN vendeur v ON r.id_vendeur = v.id where r.id_repas = ?",
            (id_repas,)
        ).fetchone()
        return resto
    except Exception as e:
        print(e)
        return False

# fonction pour obtenir les repas dun client, supprimer et rendre son repas indisponible


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
        LEFT JOIN utilisateur ON vendeur.id = utilisateur.id
        WHERE repas.disponibilite IN ('on', 1)
        AND utilisateur.actif = True
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

# fonction pour avoir les commandes dun acheteur- en seperant pour chaque restaurant


def obtenir_commandes_acheteur(id_acheteur):
    """Retourne les commandes reçues par un acheteur avec leurs repas."""
    db = get_db()

    try:
        commandes = db.execute(
            """
            SELECT
                commande.id_commande,
                commande.cout_total,
                commande.statut AS statut_general,
                vendeur.id AS id_vendeur,
                vendeur.nom_restaurant,
                commande_vendeur.statut AS statut_restaurant,
                repas.id_repas,
                repas.nom,
                repas.disponibilite,
                commande_repas.quantite,
                commande_repas.prix_unitaire
            FROM commande
            LEFT JOIN commande_repas
                ON commande.id_commande = commande_repas.id_commande
            LEFT JOIN repas
                ON commande_repas.id_repas = repas.id_repas
            LEFT JOIN vendeur
                ON repas.id_vendeur = vendeur.id
            LEFT JOIN commande_vendeur
                ON commande.id_commande = commande_vendeur.id_commande
                AND vendeur.id = commande_vendeur.id_vendeur
            WHERE commande.id_acheteur = ?
            ORDER BY commande.id_commande DESC
            """,
            (id_acheteur,)
        ).fetchall()

        return commandes

    except Exception as e:
        print(e)
        return []


def add_critique(critique):
    db = get_db()
    try:
        curseur = db.execute(
            "INSERT INTO critique (id_utilisateur,id_repas , note, id_commande )"
            "VALUES (:id_utilisateur, :id_repas, :note, :id_commande)",
            critique
        )
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_critique(id_repas):
    db = get_db()
    try:
        curseur = db.execute(
            "Select AVG(note) from critique "
            "Where id_repas = ?",
            (id_repas,)
        )
        resultat = curseur.fetchone()
        return resultat[0]
    except Exception as e:
        print(e)
        return False


def verif_critique(id_repas, id_utilisateur, id_commande):
    db = get_db()
    try:
        resultat = db.execute(
            "Select * from critique "
            "where id_repas = ? "
            "And id_utilisateur = ? "
            "and id_commande = ?", (id_repas, id_utilisateur, id_commande)).fetchone()
        return resultat

    except Exception as e:
        print(e)
        return False


def obtenir_notifications(id_acheteur):
    """Commandes terminées dont la notification n'a pas encore été vue"""
    return get_db().execute("""
        SELECT id_commande
        FROM commande
        WHERE id_acheteur = :id_acheteur
        AND statut = 'terminer'
        AND id_commande NOT IN (SELECT id_commande FROM notification_lue)
        ORDER BY id_commande DESC""",
                            {"id_acheteur": id_acheteur}).fetchall()


def marquer_notifications_lues(id_acheteur):
    """Marque comme vues les commandes terminées de l'acheteur"""
    db = get_db()
    db.execute("""
        INSERT OR IGNORE INTO notification_lue (id_commande)
        SELECT id_commande FROM commande
        WHERE id_acheteur = :id_acheteur AND statut = 'terminer'""",
               {"id_acheteur": id_acheteur})
    db.commit()


def obtenir_commandes_vendeur(id_vendeur):
    """Retourne les commandes reçues par un vendeur avec leurs repas."""
    db = get_db()

    try:
        commandes = db.execute(
            """
            SELECT
                commande.id_commande,
                ROW_NUMBER() OVER (
                    ORDER BY commande.id_commande ASC
                ) AS numero_commande,
                utilisateur.username AS nom_acheteur,
                CASE
                    WHEN commande_vendeur.statut IS NOT NULL
                    THEN commande_vendeur.statut
                    ELSE commande.statut
                END AS statut,
                repas.id_repas,
                repas.nom,
                commande_repas.quantite
            FROM commande_repas
            JOIN repas
                ON commande_repas.id_repas = repas.id_repas
            JOIN commande
                ON commande_repas.id_commande = commande.id_commande
            JOIN acheteur
                ON commande.id_acheteur = acheteur.id
            JOIN utilisateur
                ON acheteur.id = utilisateur.id
            LEFT JOIN commande_vendeur
                ON commande.id_commande = commande_vendeur.id_commande
                AND commande_vendeur.id_vendeur = repas.id_vendeur
            WHERE repas.id_vendeur = ?
            ORDER BY commande.id_commande DESC
            """,
            (id_vendeur,)
        ).fetchall()

        return commandes

    except Exception as e:
        print(e)
        return []


def modifier_statut_commande(id_commande, id_vendeur, statut):
    """Modifie le statut d'une commande pour un vendeur."""

    db = get_db()
    try:
        commande = db.execute(
            """
            SELECT 1
            FROM commande_repas
            JOIN repas
                ON commande_repas.id_repas = repas.id_repas
            WHERE commande_repas.id_commande = ?
            AND repas.id_vendeur = ?
            LIMIT 1
            """,
            (id_commande, id_vendeur)
        ).fetchone()

        if commande is None:
            return False

        association = db.execute(
            """
            SELECT id_commande
            FROM commande_vendeur
            WHERE id_commande = ?
            AND id_vendeur = ?
            """,
            (id_commande, id_vendeur)
        ).fetchone()

        if association is not None:
            db.execute(
                """
                UPDATE commande_vendeur
                SET statut = ?
                WHERE id_commande = ?
                AND id_vendeur = ?
                """,
                (statut, id_commande, id_vendeur)
            )
        else:
            db.execute(
                """
                INSERT INTO commande_vendeur
                    (id_commande, id_vendeur, statut)
                VALUES (?, ?, ?)
                """,
                (id_commande, id_vendeur, statut)
            )

        resultats = db.execute(
            """
            SELECT
                COUNT(DISTINCT repas.id_vendeur) AS total_restaurants,

                COUNT(DISTINCT CASE
                    WHEN commande_vendeur.statut = 'terminer'
                    THEN repas.id_vendeur
                END) AS restaurants_termines,

                COUNT(DISTINCT CASE
                    WHEN commande_vendeur.statut = 'cours'
                    THEN repas.id_vendeur
                END) AS restaurants_en_cours,

                COUNT(DISTINCT CASE
                    WHEN commande_vendeur.statut = 'attente'
                        OR commande_vendeur.statut IS NULL
                    THEN repas.id_vendeur
                END) AS restaurants_en_attente

            FROM commande_repas

            JOIN repas
                ON commande_repas.id_repas = repas.id_repas

            LEFT JOIN commande_vendeur
                ON commande_vendeur.id_commande = commande_repas.id_commande
                AND commande_vendeur.id_vendeur = repas.id_vendeur

            WHERE commande_repas.id_commande = ?
            """,
            (id_commande,)
        ).fetchone()

        if resultats["total_restaurants"] == resultats["restaurants_termines"]:
            statut_general = "terminer"
        elif resultats["restaurants_en_cours"] > 0  or resultats["restaurants_termines"] > 0:
            statut_general = "cours"
        else:
            statut_general = "attente"

        db.execute(
            """
            UPDATE commande
            SET statut = ?
            WHERE id_commande = ?
            """,
            (statut_general, id_commande)
        )

        db.commit()
        return True

    except Exception as e:
        print(e)
        db.rollback()
        return False


def annuler_commande(id_commande, id_acheteur):
    """Annule une commande en attente et rembourse le crédit"""
    db = get_db()
    try:
        commande = db.execute("""
            SELECT cout_total FROM commande
            WHERE id_commande = :id_commande
            AND id_acheteur = :id_acheteur
            AND statut = 'attente'
            AND id_commande NOT IN (
                SELECT id_commande FROM commande_vendeur
                WHERE statut != 'attente')""",
            {"id_commande": id_commande, "id_acheteur": id_acheteur}).fetchone()

        if commande is None:
            return False

        db.execute("DELETE FROM commande_repas WHERE id_commande = :id_commande",
                   {"id_commande": id_commande})
        db.execute("DELETE FROM commande WHERE id_commande = :id_commande",
                   {"id_commande": id_commande})
        db.execute("""UPDATE acheteur SET credit = credit + :montant
                   WHERE id = :id_acheteur""",
                   {"montant": commande["cout_total"], "id_acheteur": id_acheteur})
        db.commit()
        return True
    except Exception as e:
        print(e)
        db.rollback()
        return False
def desactiver_compte(id_utilisateur):
    db = get_db()
    try:
        db.execute(
            "Update utilisateur set actif = False "
            "Where id = ?", (id_utilisateur,))
        db.commit()
        return True
    except Exception as e:
            print(e)
            return False
