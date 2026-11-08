/**
 * Recherche de repas par nom (AJAX)
 */

/* global envoyerRequeteAjax */

"use strict"

const point = document.getElementById("point-notification")
const panneau = document.getElementById("panneau-notifications")
const listeNotifications = document.getElementById("liste-notifications")
const boutonNotifications = document.getElementById("boutonNotifications")

function ajouterMessageVide() {
    const div = document.createElement("div")
    div.className = "text-muted text-center"
    div.textContent = "Aucune notification"
    listeNotifications.appendChild(div)
}

function ajouterNotification(idCommande) {
    const carte = document.createElement("div")
    carte.className = "d-flex align-items-center gap-3 p-2 mb-1 rounded bg-light"
    carte.innerHTML = `
        <span class="fs-4">🎉</span>
        <div>
            <div class="fw-semibold">Commande #${idCommande}</div>
            <div class="small text-muted">Votre commande est terminée</div>
        </div>`
    listeNotifications.appendChild(carte)
}

async function chargerNotifications(forcer) {
    if (!forcer && panneau.classList.contains("show")) {
        return
    }

    const reponse = await fetch("/api/notifications")
    const donnees = await reponse.json()

    listeNotifications.innerHTML = ""
    if (donnees.commandes.length === 0) {
        ajouterMessageVide()
        point.classList.add("d-none")
    } else {
        for (const idCommande of donnees.commandes) {
            ajouterNotification(idCommande)
        }
        point.classList.remove("d-none")
    }
}

async function marquerCommeLues() {
    await chargerNotifications(true)
    await envoyerRequeteAjax("/api/notifications/lues", "POST")
    point.classList.add("d-none")
}

function initialisation() {
    chargerNotifications(true)
    setInterval(chargerNotifications, 10000)
    boutonNotifications.addEventListener("shown.bs.dropdown", marquerCommeLues)
}

window.addEventListener("load", initialisation)