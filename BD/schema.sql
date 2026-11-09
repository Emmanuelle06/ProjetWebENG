


CREATE TABLE IF NOT EXISTS utilisateur
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    statut TEXT NOT NULL CHECK (statut IN ('acheteur', 'vendeur')),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS acheteur
(
    id INTEGER PRIMARY KEY,
    telephone VARCHAR(10) CHECK (length(telephone) = 10) ,
    nom TEXT,
    prenom TEXT,
    adresse_postal TEXT,
    condition BOOLEAN,
    credit REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (id) REFERENCES utilisateur(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vendeur
(
    id INTEGER PRIMARY KEY,
    telephone VARCHAR(10) CHECK (length(telephone) = 10),
    nom_restaurant TEXT,
    adresse_postale TEXT,
    condition BOOLEAN,
    FOREIGN KEY (id) REFERENCES utilisateur(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS repas
(
    id_repas INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prix INTEGER,
    description TEXT NOT NULL,
    disponibilite BOOLEAN,
    image BLOB,
    id_vendeur INTEGER,
    FOREIGN KEY (id_vendeur) REFERENCES vendeur(id) ON DELETE CASCADE
);

create table IF NOT EXISTS commande
(
    id_commande INTEGER PRIMARY KEY AUTOINCREMENT,
    id_acheteur INTEGER,
    statut TEXT CHECK (statut IN ('attente', 'cours', 'terminer')),
    cout_total INTEGER,
    FOREIGN KEY (id_acheteur) REFERENCES acheteur(id) ON DELETE CASCADE
);

create table IF NOT EXISTS commande_repas
(
    id_commande INTEGER,
    id_repas INTEGER,
    quantite INTEGER,
    prix_unitaire INTEGER,

    PRIMARY KEY(id_commande, id_repas),
    FOREIGN KEY(id_commande) REFERENCES commande(id_commande),
    FOREIGN KEY(id_repas) REFERENCES repas(id_repas)
);


CREATE TABLE IF NOT EXISTS notification_lue
(
    id_commande INTEGER PRIMARY KEY,
    FOREIGN KEY (id_commande) REFERENCES commande(id_commande) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS commande_vendeur
(
    id_commande INTEGER,
    id_vendeur INTEGER,
    statut TEXT NOT NULL DEFAULT 'attente'
        CHECK (statut IN ('attente', 'cours', 'terminer')),

    PRIMARY KEY (id_commande, id_vendeur),
    FOREIGN KEY (id_commande)
        REFERENCES commande(id_commande) ON DELETE CASCADE,
    FOREIGN KEY (id_vendeur)
        REFERENCES vendeur(id) ON DELETE CASCADE
);