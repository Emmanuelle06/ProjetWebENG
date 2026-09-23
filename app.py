from flask import Flask, render_template, request

app = Flask(__name__, static_url_path='', template_folder='templates')


@app.route("/")
def bonjour():
    """Page d'accueil"""
    return render_template('accueil.jinja')


@app.route('/inscription-vendeur', methods=["GET", "POST"])
def inscription_vendeur():
    """Inscription vendeur"""
    if request.method == "GET":
        return render_template("inscription_vendeur.jinja")

    nom_restaurant = request.form.get("nom_restaurant")
    adresse = request.form.get("adresse")
    telephone = request.form.get("telephone")
    mot_de_passe = request.form.get("mot_de_passe")
    confirmation_mot_de_passe = request.form.get("confirmation_mot_de_passe")

    classe_nom_restaurant = ""
    classe_adresse = ""
    classe_telephone = ""
    classe_mot_de_passe = ""
    classe_confirmation_mot_de_passe = ""

    a_erreur = False

    if nom_restaurant == "":
        a_erreur = True
        classe_nom_restaurant = "is-invalid"
    else:
        classe_nom_restaurant = "is-valid"

    if adresse == "":
        a_erreur = True
        classe_adresse = "is-invalid"

    else:
        classe_adresse = "is-valid"

    if telephone == "":
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

    if a_erreur:
        return render_template("inscription_vendeur.jinja", nom_restaurant=nom_restaurant,
                            adresse=adresse, telephone=telephone,
                            classe_nom_restaurant=classe_nom_restaurant,
                            classe_adresse=classe_adresse, classe_telephone=classe_telephone,
                            classe_mot_de_passe=classe_mot_de_passe,
                            classe_confirmation_mot_de_passe=classe_confirmation_mot_de_passe)
    else:
        return "Compte vendeur crée avec succès"
