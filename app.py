
import hashlib
from flask import Flask, render_template,request,session,redirect,url_for
from BD import db

app = Flask(__name__, static_url_path='', template_folder='templates')
app.config['DATABASE'] = 'BD/eatfast.sqlite' #cest la ou la bd sera enregistré

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
        return redirect(url_for("menu"))

    if utilisateur["statut"] == "vendeur":
        return redirect(url_for("vendeur"))

    return redirect(url_for("index"))

@app.route("/menu")
def menu():
    if "id_utilisateur" not in session:
        return redirect(url_for("index"))

    return render_template("menu.jinja")


@app.route("/vendeur")
def vendeur():
    if "id_utilisateur" not in session:
        return redirect(url_for("index"))

    return render_template("vendeur.jinja")