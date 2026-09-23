from flask import Blueprint, render_template

bp_vendeur = Blueprint('vendeur', __name__)

@bp_vendeur.route('/ajout-repas', methods=['POST'])
def creer_repas():
    repasAAjouter = {
                "nom": "",
                "prix": "",
                "description": "",
                "dispo": "",
                "photo": "",
            } 
    
    return render_template('accueil.jinja')
