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


        nom_repas = ""
        prix_repas = ""
        desc_repas = ""
        dispo = False

        valide = True
        if request.method == 'POST':
            nom_repas = request.form.get("titre", "").strip()
            prix_repas = request.form.get("prix", "").strip()
            desc_repas = request.form.get("description", "").strip()
            if request.form.get("dispo"):
                dispo = True
            else:
                dispo = False
            photo = request.files.get("photo")

            if not nom_repas:
                classe_titre = "is-invalid"
                valide = False
                
            prix = None
            if not prix_repas:
                classe_prix = "is-invalid"
                message_prix = "Veuillez saisir un prix valide."
                valide = False
            else:
                prix = float(prix_repas)
                if prix < 0:
                    classe_prix = "is-invalid"
                    message_prix = "Veuillez saisir un prix valide."
                    valide = False

            if not desc_repas:
                classe_description = "is-invalid"
                message_description = "Veuillez saisir un prix valide."
                valide = False


            if not photo or photo.filename == "":
                classe_photo = "is-invalid"
                message_photo = "Veuillez sélectionner une photo."
                valide = False
            if valide:
                image_blob = photo.read()
                repasAAjouter = {
                    "nom": nom_repas,
                    "prix": prix,
                    "description": desc_repas,
                    "disponibilite": dispo,
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
            message_photo=message_photo,
            nom_repas=nom_repas,
            prix_repas = prix_repas,
            desc_repas=desc_repas,
            dispo=dispo
            )

def obtenir_profil(id_utilisateur):
    base_de_donnees = db.get_db()

    utilisateur = base_de_donnees.execute(
        """
        SELECT utilisateur.username,
               vendeur.nom_restaurant,
               vendeur.telephone,
               vendeur.adresse_postale
        FROM utilisateur
        JOIN vendeur ON utilisateur.id = vendeur.id
        WHERE utilisateur.id = ?
        """,
        (id_utilisateur,)
    ).fetchone()

    return utilisateur

@bp_vendeur.route('/profil')
def profil():
    if "id_utilisateur" not in session:
        return redirect("/")
    id_utilisateur = session["id_utilisateur"]
    utilisateur = obtenir_profil(id_utilisateur)

    if utilisateur is None:
        session.clear()
        return redirect("/")
    return render_template("vendeur/profil.jinja", utilisateur=utilisateur)

@bp_vendeur.route('/profil/modifier', methods=["GET", "POST"])
def modifier_profil():
    """Modification des informations du profil vendeur"""
    if "id_utilisateur" not in session:
        return redirect("/")

    id_utilisateur = session["id_utilisateur"]
    utilisateur = obtenir_profil(id_utilisateur)

    if utilisateur is None:
        session.clear()
        return redirect("/")

    if request.method == "GET":
        return render_template("vendeur/modifier_profil.jinja",
                               utilisateur=utilisateur)

    nom_utilisateur = request.form.get("nom_utilisateur", "").strip()
    nom_restaurant = request.form.get("nom_restaurant", "").strip()
    telephone = request.form.get("telephone", "").strip()
    adresse = request.form.get("adresse", "").strip()

    a_erreur = False

    if nom_utilisateur == "":
        a_erreur = True
        classe_nom_utilisateur = "is-invalid"
        message_nom_utilisateur = "Veuillez saisir un nom d'utilisateur."
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
            a_erreur = True
            classe_nom_utilisateur = "is-invalid"
            message_nom_utilisateur = "Ce nom d'utilisateur existe déjà."
        else:
            classe_nom_utilisateur = "is-valid"

    if nom_restaurant == "":
        a_erreur = True
        classe_nom = "is-invalid"
    else:
        classe_nom = "is-valid"

    if len(telephone) != 10 or not telephone.isdigit():
        a_erreur = True
        classe_telephone = "is-invalid"
    else:
        classe_telephone = "is-valid"

    if adresse == "":
        a_erreur = True
        classe_adresse = "is-invalid"
    else:
        classe_adresse = "is-valid"

    if a_erreur:
        return render_template("profil/modifier_profil.jinja",
                               utilisateur=utilisateur,
                               nom_restaurant=nom_restaurant,
                               telephone=telephone, adresse=adresse,
                               classe_nom_utilisateur=classe_nom_utilisateur,
                               classe_nom=classe_nom,
                               classe_telephone=classe_telephone,
                               classe_adresse=classe_adresse)

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
        UPDATE vendeur
        SET nom_restaurant = ?, telephone = ?, adresse_postal = ?
        WHERE id = ?
        """,
        (nom_restaurant,telephone, adresse, id_utilisateur)
    )
    base_de_donnees.commit()
    session["username"] = nom_utilisateur
    flash("Profil modifié avec succès", "success")
    return redirect("/profil", 303)


@bp_vendeur.route('/profil/supprimer', methods=["POST"])
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
