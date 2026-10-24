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

def calculer_quantite_panier():
    session["quantite_panier"] = 0
    for repas in session["panier"]:
        session["quantite_panier"] += repas["quantite"]


def chercher_repas(mot, prix_min, prix_max):
    repas = db.get_db().execute("""
        SELECT repas.id_repas, repas.nom, repas.prix, vendeur.nom_restaurant
        FROM repas
        LEFT JOIN vendeur ON repas.id_vendeur = vendeur.id
        WHERE repas.disponibilite = 'on'
        AND repas.prix >= :prix_min
        AND repas.prix <= :prix_max""",
        {"prix_min": prix_min, "prix_max": prix_max}).fetchall()

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
    ouvrir_panier = session.pop("ouvrir_panier", False)

    return render_template("menu.jinja", ouvrir_panier=ouvrir_panier)



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
        prix_max = 1000000

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
    calculer_quantite_panier()
    session["ouvrir_panier"] = True
    session.modified = True

    flash("Repas ajouté au panier.", "success")
    return redirect("/menu")

@bp_menu.route('/enlever-panier/<int:id_repas>')
def supprimer_panier(id_repas):
    for repas in session["panier"]:
        if repas["id"] == id_repas:
            session["panier"].remove(repas)
            calculer_quantite_panier()
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
        calculer_quantite_panier()
        session.modified = True
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
    calculer_quantite_panier()
    session["ouvrir_panier"] = True
    session.modified = True
    return redirect ('/menu')
