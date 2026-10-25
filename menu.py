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


def chercher_repas(mot, prix_min, prix_max):
    repas = db.obtenir_repas_disponibles(prix_min, prix_max)

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
    prix_min = request.args.get("prix_min", "")
    if prix_min.isdigit():
        prix_min = int(prix_min)
    else:
        prix_min = 0

    prix_max = request.args.get("prix_max", "")
    if prix_max.isdigit():
        prix_max = int(prix_max)
    else:
        prix_max = 10000

    resultats = []
    for r in chercher_repas(mot, prix_min, prix_max):
        resultats.append({
            "id_repas": r["id_repas"],
            "nom": r["nom"],
            "prix": r["prix"],
            "nom_restaurant": r["nom_restaurant"],
            "image_url": "/image-repas/" + str(r["id_repas"])
        })

    return jsonify({"resultats": resultats, "total": len(resultats)})



@bp_menu.route('/ajout-panier/<int:id_repas>')
def ajouter_panier(id_repas):
    repas = db.get_repas(id_repas)
    resto = db.get_restaurant(id_repas)
    if "panier" not in session:
        session["panier"] = []
    indicateur = False
    session["cout"] = 0
    for item in session["panier"]:
        session["cout"] += item["prix"]
        if item["id"] == repas["id_repas"]:
            item["quantite"] += 1
            indicateur = True
            break

    if indicateur == False:
        session["panier"].append({
             "id": repas["id_repas"],
            "nom": repas["nom"],
            "prix": repas["prix"],
            "quantite": 1,
            "nom_resto": resto["nom_restaurant"]
            })
    session["cout"] = 0

    for item in session["panier"]:
        session["cout"] += item["prix"] * item["quantite"]
    session.modified = True

    flash("Repas ajouté au panier.", "success")
    return redirect("/menu")

@bp_menu.route('/enlever-panier/<int:id_repas>')
def supprimer_panier(id_repas):
    for repas in session["panier"]:
        if repas["id"] == id_repas:
            session["panier"].remove(repas)
            session.modified = True
            # flash("Repas supprimé avec succès", "success")
            break
    session["cout"] = 0
    for item in session["panier"]:
        session["cout"] += item["prix"] * item["quantite"]
    return redirect("/menu")



@bp_menu.route('/vider-panier',methods=["POST"])
def vider_panier():
    if session:
        session["panier"] = []
        flash("Panier vidé avec succès", "success")
        session["cout"] = 0
        for item in session["panier"]:
            session["cout"] += item["prix"] * item["quantite"]
        return redirect('/menu')
    else:
        abort(401)

@bp_menu.route('/modifier-quantite/<int:id_repas>', methods=['POST'])
def modifier_quantite(id_repas):
    action = request.form.get("action")

    for repas in session["panier"]:
        if repas["id"] == id_repas:
            if action == "plus":
                repas["quantite"] += 1
            elif action == "moins":
                repas["quantite"] -= 1
                if  repas["quantite"] <= 0:
                    session["panier"].remove(repas)
            break
    session["cout"] = 0
    for item in session["panier"]:
        session["cout"] += item["prix"] * item["quantite"]
    session.modified = True
    return redirect ('/menu')



@bp_menu.route('/repas/<int:id_repas>')
def detail_repas(id_repas):
    if "id_utilisateur" not in session:
        flash("Veuillez vous connecter.", "warning")
        return redirect("/")

    repas = db.obtenir_repas_par_id(id_repas)

    if repas is None:
        abort(404)

    return render_template("detail_repas.jinja", repas=repas)
