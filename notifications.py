from flask import Blueprint, session, abort, jsonify
from BD import db

bp_notifications = Blueprint('notifications', __name__)


@bp_notifications.route('/api/notifications', methods=["GET"])
def api_notifications():
    """Retourne les numéros des commandes terminées non vues de l'acheteur"""
    if session.get("statut") != "acheteur":
        abort(403)

    notifications = db.obtenir_notifications(session["id_utilisateur"])
    ids = [n["id_commande"] for n in notifications]
    return jsonify({"commandes": ids})


@bp_notifications.route('/api/notifications/lues', methods=["POST"])
def api_notifications_lues():
    """Marque les notifications comme vues"""
    if session.get("statut") != "acheteur":
        abort(403)

    db.marquer_notifications_lues(session["id_utilisateur"])
    return jsonify({"ok": True})