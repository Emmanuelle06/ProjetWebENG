from flask import Blueprint, render_template, request, session, redirect, flash, abort
from BD import db

bp_vendeur = Blueprint('vendeur', __name__)

@bp_vendeur.route('/ajout-repas', methods=['GET', 'POST'])
def creer_repas():
    if "id_utilisateur" not in session:
        flash("Vous devez être connecté pour ajouter un repas.", "warning")
        return redirect("/")
    if session.get("statut") != "vendeur":
        abort(403)
    else:
        classe_titre = ""
        classe_prix = ""
        classe_description = ""
        classe_dispo = ""
        classe_photo = ""


        message_prix = ""
        message_description = ""
        message_dispo = ""
        message_photo = ""
        valide = True
        if request.method == 'POST':
            photo = request.files.get("photo")
            prix = request.form.get("prix")

            if not request.form.get("titre"):
                classe_titre = "is-invalid"
                valide = False

            if not prix:
                classe_prix = "is-invalid"
                message_prix = "Veuillez saisir un prix valide."
                valide = False
            else:
                prix = float(prix)
                if prix < 0:
                    classe_prix = "is-invalid"
                    message_prix = "Veuillez saisir un prix valide."
                    valide = False

            if not request.form.get("description"):
                classe_description = "is-invalid"
                valide = False


            if not photo or photo.filename == "":
                classe_photo = "is-invalid"
                message_photo = "Veuillez sélectionner une photo."
                valide = False
            if valide:
                image_blob = photo.read()
                repasAAjouter = {
                    "nom": request.form.get("titre"),
                    "prix": prix,
                    "description": request.form.get("description"),
                    "disponibilite": request.form.get("dispo"),
                    "image" : image_blob,
                    "id_vendeur": session["id_utilisateur"]
                    }

                condition = db.add_repas(repasAAjouter)
                if condition == True:
                    flash("Repas créé avec succès", "success")
                    return render_template('page_vendeur.jinja')
                else:
                    print('ERREUR')
        return render_template('vendeur/ajout-repas.jinja', classe_titre=classe_titre,
            classe_prix=classe_prix,
            classe_description=classe_description,
            classe_dispo=classe_dispo,
            classe_photo=classe_photo,
            message_prix=message_prix,
            message_description=message_description,
            message_dispo=message_dispo,
            message_photo=message_photo)
