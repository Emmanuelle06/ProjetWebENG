/**
 * Recupère et active le deplacement de toutes les commandes
 */

/* global envoyerRequeteAjax */

"use strict";

const colonnes = document.querySelectorAll(".kanban-zone");

colonnes.forEach(function (colonne) {

    new Sortable(colonne, {
        group: "commandes",
        animation: 150,
        draggable: ".kanban-carte",

        onEnd: async function (evenement) {

            document.getElementById("compteur-attente").textContent =
                document.querySelectorAll("#repas-a-realiser .kanban-carte").length;

            document.getElementById("compteur-cours").textContent =
                document.querySelectorAll("#repas-en-cours .kanban-carte").length;

            document.getElementById("compteur-terminer").textContent =
                document.querySelectorAll("#repas-prets .kanban-carte").length;

            try {
                await envoyerRequeteAjax(
                    "/vendeur/commande/statut",
                    "POST",
                    {
                        id_commande: evenement.item.dataset.idCommande,
                        statut: evenement.to.dataset.statut
                    }
                );
            } catch (erreur) {
                console.log("Erreur lors de la modification du statut :", erreur);
                location.reload();
            }

        }
    });

});
