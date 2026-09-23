from flask import Flask, render_template
from BD import db

app = Flask(__name__, static_url_path='', template_folder='templates')
app.config['DATABASE'] = 'BD/eatfast.sqlite' #cest la ou la bd sera enregistré

db.init_app(app)

@app.route("/")
def bonjour():
    """Page d'accueil"""
    return render_template('accueil.jinja')
