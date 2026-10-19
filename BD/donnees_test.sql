-- mot de passe 1234
INSERT OR IGNORE INTO utilisateur (username, mot_de_passe, statut) VALUES
('marco',  'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db', 'vendeur'),
('zen',    'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db', 'vendeur'),
('burger', 'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db', 'vendeur');

INSERT OR IGNORE INTO vendeur (id, telephone, nom_restaurant, adresse_postale, condition) VALUES
((SELECT id FROM utilisateur WHERE username = 'marco'),  '5141234567', 'Chez Marco',   '123 rue Sainte-Catherine, Montréal', 1),
((SELECT id FROM utilisateur WHERE username = 'zen'),    '5142345678', 'Sushi Zen',    '456 avenue du Parc, Montréal',       1),
((SELECT id FROM utilisateur WHERE username = 'burger'), '5143456789', 'Burger House', '789 boulevard Saint-Laurent, Montréal', 1);
