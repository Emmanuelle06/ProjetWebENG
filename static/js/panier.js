"use strict";

console.log("panier.js chargé");
console.log("ouvrirPanier =", ouvrirPanier);

if (ouvrirPanier) {
    const boutonPanier = document.getElementById("boutonPanier");

    console.log("Bouton panier =", boutonPanier);

    if (boutonPanier) {
        boutonPanier.click();
    }
}