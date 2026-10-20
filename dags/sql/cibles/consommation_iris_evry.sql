-- Cible : Consommation_IRIS_Evry (ID_IRIS, Conso_moyenne_annuelle)
-- s4.iris mélange Paris et Evry : on ne garde que les IRIS d'Evry (id_ville = nom de ville).
-- s2.consommation ne contient qu'Evry, la ville n'est donc pas comparée dans la jointure.
-- id_rue est en casse mixte ("aguado", "PABLO NERUDA") et sans type de voie, alors que
-- nom_rue l'inclut ("BOULEVARD AGUADO") : on compare en minuscules et on vérifie que
-- nom_rue se termine par id_rue (mot entier, grâce à l'espace ajoutée devant).
-- Correction du rapport : jointure sur iris_evry.id_rue (et non IRIS_Paris.ID_Rue).
DROP TABLE IF EXISTS cible.consommation_iris_evry;
CREATE TABLE cible.consommation_iris_evry AS WITH iris_evry AS (
    SELECT lower(trim(id_rue)) AS rue,
        id_iris
    FROM s4.iris
    WHERE id_ville = 'Evry-Courcouronnes'
)
SELECT i.id_iris,
    avg(c.nb_kw_jour * 365) AS conso_moyenne_annuelle
FROM iris_evry i
    JOIN s2.consommation c
        ON right(' ' || lower(trim(c.nom_rue)), length(i.rue) + 1) = ' ' || i.rue
GROUP BY i.id_iris;
ALTER TABLE cible.consommation_iris_evry ADD PRIMARY KEY (id_iris);
