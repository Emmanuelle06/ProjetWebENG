from flask import Blueprint, render_template, request, session
from BD import db

bp_vendeur = Blueprint('vendeur', __name__)

@bp_vendeur.route('/ajout-repas', methods=['GET', 'POST'])
def creer_repas():
    if request.method == 'POST':
        photo = request.files.get("photo")
        image_blob = photo.read()
        repasAAjouter = {
            "nom": request.form.get("titre"),
            "prix": request.form.get("prix"),
            "description": request.form.get("description"),
            "disponibilite": request.form.get("dispo"),
            "image" : image_blob,
            # "id_vendeur" : session["id_vendeur"] 
            }
        print(repasAAjouter)     
        condition = db.add_repas(repasAAjouter)
        if condition == True:
            print('REUSSI')
            return render_template('accueil.jinja')
        else:
            print('ERREUR')
    return render_template('vendeur/ajout-repas.jinja')
