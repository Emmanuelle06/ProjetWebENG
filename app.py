import hashlib
from flask import Flask, render_template,request,flash
from BD import db

app = Flask(__name__, static_url_path='', template_folder='templates')
app.config['DATABASE'] = 'BD/eatfast.sqlite' #cest la ou la bd sera enregistré

db.init_app(app)

@app.route("/")
def bonjour():
    """Page d'accueil"""
    return render_template('accueil.jinja')

@app.route('/inscription-acheteur', methods=["GET", "POST"])
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

    classe_nom=""
    classe_prenom =""
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
        return render_template("inscription_vendeur.jinja",
                            nom = nom, prenom=prenom,
                            nom_utilisateur=nom_utilisateur,
                            adresse=adresse, telephone=telephone,
                            classe_nom_utilisateur=classe_nom_utilisateur,
                            message_nom_utilisateur=message_nom_utilisateur,classe_nom=classe_nom,
                            classe_adresse=classe_adresse, classe_telephone=classe_telephone,
                            classe_prenom=classe_prenom,classe_mot_de_passe=classe_mot_de_passe,
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

        base_de_donnees.execute("""INSERT INTO acheteur (id,nom_restaurant, adresse_postale, telephone, condition)
                                VALUES (:id, :nom_restaurant, :adresse, :telephone, :condition)""",
                                {
                                    "id":id_utilisateur,
                                    "adresse": adresse,
                                    "telephone": telephone,
                                    "condition": True
                                }
)
        base_de_donnees.commit()

        flash("Compte vendeur crée avec succès")
        return "Compte vendeur créé avec succès ! (redirection vers le menu à venir)"