DROP TABLE IF EXISTS acheteur;
DROP TABLE IF EXISTS utilisateur;


CREATE TABLE utilisateur
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    statut TEXT NOT NULL CHECK (statut IN ('acheteur', 'vendeur')),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE acheteur
(
    id INTEGER PRIMARY KEY,
    telephone VARCHAR(10) CHECK (length(telephone) = 10) ,
    nom TEXT,
    prenom TEXT,
    code_postal TEXT,
    FOREIGN KEY (id) REFERENCES utilisateur(id) ON DELETE CASCADE
);

create table vendeur(
id_vendeur int primary key
);

CREATE TABLE repas
(
id_repas integer primary KEY, 
nom TEXT Not null,
prix INTEGER,
description TEXT not null,
disponibilite BOOLEAN,
image BLOB,
id_restaurant INTEGER,
FOREIGN KEY (id_restaurant) REFERENCES restaurant(id) ON DELETE CASCADE
);
