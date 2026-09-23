from flask import Flask, render_template
from vendeur import bp_vendeur
app = Flask(__name__, static_url_path='', template_folder='templates')


# @app.route("/")
# def bonjour():
#     """Page d'accueil"""
#     return render_template('accueil.jinja')

@app.route("/")
def bonjour():
    """Page d'accueil"""
    return render_template('ajout-repas.jinja')

