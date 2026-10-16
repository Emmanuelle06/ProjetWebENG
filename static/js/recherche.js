/**
 * Recherche de repas par nom (AJAX)
 */

/* global envoyerRequeteAjax */

"use strict"


const listeRepas = document.getElementById("liste-repas")
const messageAucun = document.getElementById("message-aucun")


/**
 * Construit la carte d'un repas et l'ajoute à la grille.
 */
function ajouterCarte(repas) {
    const col = document.createElement("div")
    col.className = "col-6 col-md-3"

    const carte = document.createElement("div")
    carte.className = "carte-repas"

    const image = document.createElement("img")
    image.src = repas.image_url
    image.alt = repas.nom
    image.className = "image-repas"

    const info = document.createElement("div")
    info.className = "info-repas"

    const nom = document.createElement("p")
    nom.className = "nom-repas mb-0"
    nom.textContent = repas.nom

    const restaurant = document.createElement("p")
    restaurant.className = "nom-resto-repas mb-2"
    restaurant.textContent = repas.nom_restaurant || "Restaurant inconnu"

    const ligne = document.createElement("div")
    ligne.className = "d-flex justify-content-between align-items-center"

    const prix = document.createElement("span")
    prix.className = "prix-repas"
    prix.textContent = repas.prix + "$ CA"

    const bouton = document.createElement("a")
    bouton.href = "#"
    bouton.className = "btn-ajouter"
    bouton.textContent = "+"

    ligne.append(prix, bouton)
    info.append(nom, restaurant, ligne)
    carte.append(image, info)
    col.append(carte)
    listeRepas.append(col)
}


/**
 * Demande les repas au serveur selon le mot saisi, puis les affiche.
 */
async function chargerRepas() {
    const parametres = {
        "mot": document.getElementById("mot").value.trim()
    }

    const donnees = await envoyerRequeteAjax("/api/recherche", "GET", parametres)

    listeRepas.replaceChildren()
    for (const repas of donnees.resultats) {
        ajouterCarte(repas)
    }

    messageAucun.classList.toggle("d-none", donnees.resultats.length > 0)
}


/**
 * Appelée au clic sur « Rechercher » ou en appuyant sur Entrée :
 * on empêche le rechargement de la page et on lance la recherche.
 */
function gererSubmit(evenement) {
    evenement.preventDefault()
    chargerRepas()
}


/**
 * Appelée lors de l'initialisation de la page
 */
function initialisation() {
    chargerRepas()

    document.getElementById("mot").addEventListener("input", chargerRepas)
    document.getElementById("form-recherche").addEventListener("submit", gererSubmit)
}

window.addEventListener("load", initialisation)