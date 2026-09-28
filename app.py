import os
import hashlib
from flask import Flask, render_template, request, redirect, flash,session,url_for
from BD import db

app = Flask(__name__, static_url_path='', template_folder='templates')
app.config['DATABASE'] = 'BD/eatfast.sqlite' #cest la ou la bd sera enregistré
app.secret_key = "b37bbe5bbd0b222206d7a811ad4c612cf5267966bb993cd250db389deaf7c279"

db.init_app(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("accueil.jinja")

    nom_utilisateur = request.form.get("username", "").strip()
    mot_de_passe = request.form.get("password", "")
    statut = request.form.get("statut", "")

    mot_de_passe_hache = hashlib.sha512(mot_de_passe.encode()).hexdigest()

    base_de_donnees = db.get_db()
    utilisateur = base_de_donnees.execute(
        """SELECT id, statut FROM utilisateur
           WHERE username = ? AND mot_de_passe = ? AND statut = ?""",
        (nom_utilisateur, mot_de_passe_hache, statut)
    ).fetchone()

    if utilisateur is None:
        return render_template("accueil.jinja",
                               nom_utilisateur=nom_utilisateur,
                               statut=statut,
                               message_erreur="Nom d'utilisateur, mot de passe ou statut incorrect.")

    session.clear()
    session["id_utilisateur"] = utilisateur["id"]
    session["statut"] = utilisateur["statut"]
    if utilisateur["statut"] == "acheteur":
        return redirect('/menu',303)

    if utilisateur["statut"] == "vendeur":
        return redirect('/vendeur',303)

    return redirect('/',303)


@app.route('/inscription-vendeur', methods=["GET", "POST"])
def inscription_vendeur():
    """Inscription vendeur"""
    if request.method == "GET":
        return render_template("inscription_vendeur.jinja")

    nom_restaurant = request.form.get("nom_restaurant","").strip()
    nom_utilisateur = request.form.get("nom_utilisateur", "").strip()
    adresse = request.form.get("adresse","").strip()
    telephone = request.form.get("telephone","").strip()
    mot_de_passe = request.form.get("mot_de_passe","").strip()
    confirmation_mot_de_passe = request.form.get("confirmation_mot_de_passe","").strip()
    condition = request.form.get("condition","").strip()

    classe_nom_restaurant = ""
    classe_nom_utilisateur = ""
    classe_adresse = ""
    classe_telephone = ""
    classe_mot_de_passe = ""
    classe_confirmation_mot_de_passe = ""
    classe_condition = ""

    message_nom_utilisateur = "Veuillez saisir un nom d'utilisateur."

    a_erreur = False

    if nom_restaurant == "":
        a_erreur = True
        classe_nom_restaurant = "is-invalid"
    else:
        classe_nom_restaurant = "is-valid"


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
        return render_template("inscription_vendeur.jinja", nom_restaurant=nom_restaurant,
                            nom_utilisateur=nom_utilisateur,
                            adresse=adresse, telephone=telephone,
                            classe_nom_restaurant=classe_nom_restaurant,
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
                                    "statut": "vendeur"
                                }
)
        id_utilisateur = base_de_donnees.execute("SELECT last_insert_rowid()").fetchone()[0]

        base_de_donnees.execute("""INSERT INTO vendeur (id,nom_restaurant, adresse_postale, telephone, condition)
                                VALUES (:id, :nom_restaurant, :adresse, :telephone, :condition)""",
                                {
                                    "id":id_utilisateur,
                                    "nom_restaurant": nom_restaurant,
                                    "adresse": adresse,
                                    "telephone": telephone,
                                    "condition": True
                                }
)
        base_de_donnees.commit()

        flash("Compte vendeur crée avec succès")
        return redirect("/", 303)

@app.route('/menu', methods=["GET", "POST"])
def menu():
    return render_template("menu.jinja")

@app.route("/vendeur")
def vendeur():
    if "id_utilisateur" not in session:
        return redirect(url_for("index"))

    return render_template("page_vendeur.jinja")
