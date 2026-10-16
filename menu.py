import unicodedata
from flask import Blueprint, render_template, request, session, redirect, flash, abort, jsonify
from BD import db

bp_menu = Blueprint('menu', __name__)


def normaliser(texte):
    """Met en minuscules et retire les accents : 'Gâteau' correspond à 'gateau'"""
    texte = texte.replace("œ", "oe").replace("Œ", "oe")
    texte = unicodedata.normalize("NFD", texte)
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return texte.lower()


def chercher_repas(mot):
    """Retourne les repas disponibles dont le nom correspond au mot cherché"""
    repas = db.get_db().execute(
        """SELECT repas.id_repas, repas.nom, repas.prix, vendeur.nom_restaurant
           FROM repas
           LEFT JOIN vendeur ON repas.id_vendeur = vendeur.id
           WHERE repas.disponibilite = 'on'"""
    ).fetchall()

    if mot:
        mot_normalise = normaliser(mot)
        repas = [r for r in repas if mot_normalise in normaliser(r["nom"])]

    return repas


@bp_menu.route('/menu', methods=["GET"])
def menu():
    """Affiche la page du menu (les repas sont chargés en AJAX)"""
    if "id_utilisateur" not in session:
        flash("Vous devez être connecté pour accéder au menu.", "warning")
        return redirect("/")

    return render_template("menu.jinja")



@bp_menu.route('/api/recherche', methods=["GET"])
def api_recherche():
    """Retourne en JSON les repas correspondant à la recherche (appelée en AJAX)"""
    if "id_utilisateur" not in session:
        abort(403)

    mot = request.args.get("mot", "").strip()

    resultats = []
    for r in chercher_repas(mot):
        resultats.append({
            "id_repas": r["id_repas"],
            "nom": r["nom"],
            "prix": r["prix"],
            "nom_restaurant": r["nom_restaurant"],
            "image_url": "/image-repas/" + str(r["id_repas"])
        })

    return jsonify({"resultats": resultats, "total": len(resultats)})

