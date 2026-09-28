DROP TABLE IF EXISTS acheteur;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS vendeur;


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
    adresse_postal TEXT,
    FOREIGN KEY (id) REFERENCES utilisateur(id) ON DELETE CASCADE
);


CREATE TABLE vendeur
(
    id INTEGER PRIMARY KEY,
    telephone VARCHAR(10) CHECK (length(telephone) = 10),
    nom_restaurant TEXT,
    adresse_postale TEXT,
    condition BOOLEAN,
    FOREIGN KEY (id) REFERENCES utilisateur(id) ON DELETE CASCADE
);

DELETE FROM vendeur WHERE nom_restaurant = "gla";
