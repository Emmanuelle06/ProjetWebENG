import hashlib
from flask import Blueprint, render_template, request, redirect, flash,session,url_for,abort
from BD import db

bp_acheteur = Blueprint('acheteur', __name__)

def obtenir_profil(id_utilisateur):
    base_de_donnees = db.get_db()

    utilisateur = base_de_donnees.execute(
        """
        SELECT utilisateur.username,
               acheteur.nom,
               acheteur.prenom,
               acheteur.telephone,
               acheteur.adresse_postal,
               acheteur.credit
        FROM utilisateur
        JOIN acheteur ON utilisateur.id = acheteur.id
        WHERE utilisateur.id = ?
        """,
        (id_utilisateur,)
    ).fetchone()

    return utilisateur

@bp_acheteur.route('/profil')
def profil():
    if "id_utilisateur" not in session:
        return redirect("/")
    id_utilisateur = session["id_utilisateur"]
    utilisateur = obtenir_profil(id_utilisateur)

    if utilisateur is None:
        session.clear()
        return redirect("/")
    commandes = db.obtenir_commandes_acheteur(id_utilisateur)
    return render_template("profil/profil.jinja", utilisateur=utilisateur,commandes=commandes)

@bp_acheteur.route('/inscription-acheteur', methods=["GET", "POST"])
def inscription_acheteur():
    """Inscription acheteur"""
    if request.method == "GET":
        return render_template("inscription_acheteur.jinja")

    nom = request.form.get("nom","").strip()
    prenom = request.form.get("prenom","").strip()
    nom_utilisateur = request.form.get("nom_utilisateur", "").strip()
    adresse = request.form.get("adresse","").strip()
    telephone = request.form.get("telephone","").strip()
    mot_de_passe = request.form.get("mot_de_passe","").strip()
    confirmation_mot_de_passe = request.form.get("confirmation_mot_de_passe","").strip()
    condition = request.form.get("condition","").strip()

    classe_nom = ""
    classe_prenom = ""
    classe_nom_utilisateur = ""
    classe_adresse = ""
    classe_telephone = ""
    classe_mot_de_passe = ""
    classe_confirmation_mot_de_passe = ""
    classe_condition = ""

    message_nom_utilisateur = "Veuillez saisir un nom d'utilisateur."

    a_erreur = False

    if nom == "":
        a_erreur = True
        classe_nom = "is-invalid"
    else:
        classe_nom = "is-valid"

    if prenom == "":
        a_erreur = True
        classe_prenom = "is-invalid"
    else:
        classe_prenom = "is-valid"

    if nom_utilisateur == "":
        a_erreur = True
        classe_nom_utilisateur = "is-invalid"
        message_nom_utilisateur = "Veuillez saisir un nom d'utilisateur."
    else:
        base_de_donnees = db.get_db()
        existe_deja = base_de_donnees.execute(
            "SELECT id FROM utilisateur WHERE username = ?", (nom_utilisateur,)
        ).fetchone()
        if existe_deja is not None:
            a_erreur = True
            classe_nom_utilisateur = "is-invalid"
            message_nom_utilisateur = "Ce nom d'utilisateur existe déjà."
        else:
            classe_nom_utilisateur = "is-valid"


    if adresse == "":
        a_erreur = True
        classe_adresse = "is-invalid"

    else:
        classe_adresse = "is-valid"

    if len(telephone) != 10 or not telephone.isdigit():
        a_erreur = True
        classe_telephone = "is-invalid"
    else:
        classe_telephone = "is-valid"

    if mot_de_passe == "":
        a_erreur = True
        classe_mot_de_passe = "is-invalid"
    else:
        classe_mot_de_passe = "is-valid"

    if confirmation_mot_de_passe == "" or confirmation_mot_de_passe != mot_de_passe:
        a_erreur = True
        classe_confirmation_mot_de_passe = "is-invalid"
    else:
        classe_confirmation_mot_de_passe = "is-valid"
    if condition != "on":
        a_erreur = True
        classe_condition = "is-invalid"
    else:
        classe_condition = "is-valid"

    if a_erreur:
        return render_template("inscription_acheteur.jinja", nom=nom,
                            prenom=prenom,
                            nom_utilisateur=nom_utilisateur,
                            adresse=adresse, telephone=telephone,
                            classe_nom=classe_nom,
                            classe_prenom=classe_prenom,
                            classe_nom_utilisateur=classe_nom_utilisateur,
                            message_nom_utilisateur=message_nom_utilisateur,
                            classe_adresse=classe_adresse, classe_telephone=classe_telephone,
                            classe_mot_de_passe=classe_mot_de_passe,
                            classe_confirmation_mot_de_passe=classe_confirmation_mot_de_passe,
                            classe_condition=classe_condition)
    else:
        mot_de_passe_hache = hashlib.sha512(mot_de_passe.encode()).hexdigest()

        base_de_donnees = db.get_db()

        base_de_donnees.execute("""INSERT INTO utilisateur (username, mot_de_passe, statut)
                                VALUES (:username, :mot_de_passe, :statut)""",
                                {
                                    "username": nom_utilisateur,
                                    "mot_de_passe": mot_de_passe_hache,
                                    "statut": "acheteur"
                                }
)
        id_utilisateur = base_de_donnees.execute("SELECT last_insert_rowid()").fetchone()[0]

        base_de_donnees.execute("""INSERT INTO acheteur (id,nom,prenom, adresse_postal, telephone, condition)
                                VALUES (:id, :nom, :prenom, :adresse, :telephone, :condition)""",
                                {
                                    "id":id_utilisateur,
                                    "nom": nom,
                                    "prenom":prenom,
                                    "adresse": adresse,
                                    "telephone": telephone,
                                    "condition": True
                                }
)
        base_de_donnees.commit()

        flash("Compte acheteur crée avec succès", "success")
        return redirect("/", 303)

@bp_acheteur.route('/profil/modifier', methods=["GET", "POST"])
def modifier_profil():
    """Modification des informations du profil acheteur."""
    if "id_utilisateur" not in session:
        return redirect("/")

    if session.get("statut") != "acheteur":
        abort(403)

    id_utilisateur = session["id_utilisateur"]
    utilisateur = obtenir_profil(id_utilisateur)

    if utilisateur is None:
        session.clear()
        return redirect("/")

    if request.method == "GET":
        return render_template(
            "profil/modifier_profil.jinja",
            utilisateur=utilisateur
        )

    nom_utilisateur = request.form.get("nom_utilisateur", "").strip()
    nom = request.form.get("nom", "").strip()
    prenom = request.form.get("prenom", "").strip()
    telephone = request.form.get("telephone", "").strip()
    adresse = request.form.get("adresse", "").strip()

    classe_nom_utilisateur = ""
    classe_nom = ""
    classe_prenom = ""
    classe_telephone = ""
    classe_adresse = ""

    message_nom_utilisateur = ""
    a_erreur = False

    if nom_utilisateur == "":
        classe_nom_utilisateur = "is-invalid"
        message_nom_utilisateur = "Veuillez saisir un nom d'utilisateur."
        a_erreur = True
    else:
        base_de_donnees = db.get_db()

        utilisateur_existant = base_de_donnees.execute(
            """
            SELECT id
            FROM utilisateur
            WHERE username = ? AND id != ?
            """,
            (nom_utilisateur, id_utilisateur)
        ).fetchone()

        if utilisateur_existant is not None:
            classe_nom_utilisateur = "is-invalid"
            message_nom_utilisateur = "Ce nom d'utilisateur existe déjà."
            a_erreur = True
        else:
            classe_nom_utilisateur = "is-valid"

    if nom == "":
        classe_nom = "is-invalid"
        a_erreur = True
    else:
        classe_nom = "is-valid"

    if prenom == "":
        classe_prenom = "is-invalid"
        a_erreur = True
    else:
        classe_prenom = "is-valid"

    if len(telephone) != 10 or not telephone.isdigit():
        classe_telephone = "is-invalid"
        a_erreur = True
    else:
        classe_telephone = "is-valid"

    if adresse == "":
        classe_adresse = "is-invalid"
        a_erreur = True
    else:
        classe_adresse = "is-valid"

    if a_erreur:
        utilisateur = dict(utilisateur)
        utilisateur["username"] = nom_utilisateur
        utilisateur["nom"] = nom
        utilisateur["prenom"] = prenom
        utilisateur["telephone"] = telephone
        utilisateur["adresse_postal"] = adresse

        return render_template(
            "profil/modifier_profil.jinja",
            utilisateur=utilisateur,
            classe_nom_utilisateur=classe_nom_utilisateur,
            classe_nom=classe_nom,
            classe_prenom=classe_prenom,
            classe_telephone=classe_telephone,
            classe_adresse=classe_adresse,
            message_nom_utilisateur=message_nom_utilisateur
        )

    base_de_donnees = db.get_db()

    base_de_donnees.execute(
        """
        UPDATE utilisateur
        SET username = ?
        WHERE id = ?
        """,
        (nom_utilisateur, id_utilisateur)
    )

    base_de_donnees.execute(
        """
        UPDATE acheteur
        SET nom = ?, prenom = ?, telephone = ?, adresse_postal = ?
        WHERE id = ?
        """,
        (nom, prenom, telephone, adresse, id_utilisateur)
    )

    base_de_donnees.commit()
    session["username"] = nom_utilisateur

    flash("Profil modifié avec succès.", "success")

    return redirect(url_for("acheteur.profil"), 303)


@bp_acheteur.route('/profil/supprimer', methods=["POST"])
def supprimer_profil():
    if "id_utilisateur" not in session:
        return redirect("/")

    id_utilisateur = session["id_utilisateur"]
    base_de_donnees = db.get_db()
    base_de_donnees.execute(
        "DELETE FROM utilisateur WHERE id = ?",
        (id_utilisateur,)
    )
    base_de_donnees.commit()
    session.clear()
    flash("Votre compte a été supprimé.", "success")

    return redirect("/", 303)


@bp_acheteur.route('/profil/charger-carte', methods=["POST"])
def charger_carte():
    """Permet de charger la carte de fidélité."""

    if "id_utilisateur" not in session:
        return redirect("/")

    if session.get("statut") != "acheteur":
        abort(403)

    montant_saisi = request.form.get("montant", "").strip()
    erreur_montant = ""

    try:
        montant = float(montant_saisi)

        if not 0 < montant <= 500:
            erreur_montant = "Le montant doit être supérieur à 0 et ne pas dépasser 500 $."

    except ValueError:
        montant = 0
        erreur_montant = "Veuillez saisir un montant valide."

    if erreur_montant != "":
        id_utilisateur = session["id_utilisateur"]
        utilisateur = obtenir_profil(id_utilisateur)

        return render_template(
            "profil/profil.jinja",
            utilisateur=utilisateur,
            erreur_montant=erreur_montant,
            montant=montant_saisi
        )

    base_de_donnees = db.get_db()

    base_de_donnees.execute(
        """
        UPDATE acheteur
        SET credit = credit + ?
        WHERE id = ?
        """,
        (montant, session["id_utilisateur"])
    )

    base_de_donnees.commit()

    flash(
        "Votre carte de fidélité a été chargée avec succès.",
        "success"
    )

    return redirect(url_for("acheteur.profil"), 303)
