function mettreAJourCompteurs() {
    document.querySelectorAll(".kanban-zone").forEach(function (zone) {
        const nb = zone.querySelectorAll(".kanban-carte").length;
        document.getElementById("compteur-" + zone.dataset.statut).textContent = nb;
    });
}

document.querySelectorAll(".kanban-zone").forEach(function (colonne) {

    new Sortable(colonne, {
        group: "commandes",
        animation: 150,
        draggable: ".kanban-carte",

        onEnd: function (evt) {
            if (evt.from === evt.to) return;

            const idCommande = evt.item.dataset.idCommande;
            const nouveauStatut = evt.to.dataset.statut;

            mettreAJourCompteurs();

            fetch("/vendeur/changer-statut-commande/" + idCommande, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ statut: nouveauStatut })
            })
            .then(function (reponse) {
                if (!reponse.ok) throw new Error("Erreur serveur");
            })
            .catch(function () {
                evt.from.insertBefore(evt.item, evt.from.children[evt.oldIndex]);
                mettreAJourCompteurs();
                alert("Impossible de changer le statut de la commande.");
            });
        }
    });

});