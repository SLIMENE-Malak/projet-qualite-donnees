-- Cible : Consommation_IRIS_Paris (ID_IRIS, Conso_moyenne_annuelle)
-- s4.iris mélange Paris et Evry : on ne garde que les IRIS de Paris (id_ville = nom de ville).
-- s1.consommation ne contient que Paris, la ville n'est donc pas comparée dans la jointure.
-- id_rue et nom_rue sont écrits de la même façon, sans type de voie ("ARTHUR GROUSSIER") :
-- une égalité en minuscules suffit.
-- Une rue rattachée à deux IRIS (BROCA) compte ses logements dans les deux : la source
-- ne permet pas de les départager, c'est un constat d'audit.
DROP TABLE IF EXISTS cible.consommation_iris_paris;
CREATE TABLE cible.consommation_iris_paris AS WITH iris_paris AS (
    SELECT lower(trim(id_rue)) AS rue,
        id_iris
    FROM s4.iris
    WHERE id_ville = 'Paris'
)
SELECT i.id_iris,
    avg(c.nb_kw_jour * 365) AS conso_moyenne_annuelle
FROM iris_paris i
    JOIN s1.consommation c ON lower(trim(c.nom_rue)) = i.rue
GROUP BY i.id_iris;
ALTER TABLE cible.consommation_iris_paris ADD PRIMARY KEY (id_iris);
