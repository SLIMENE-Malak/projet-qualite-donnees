-- Cible : Consommation_IRIS_Evry (ID_IRIS, Conso_moyenne_annuelle)
-- Dans s4.iris, id_ville contient le code postal (91000...) et id_rue le nom de rue
-- en minuscules : la jointure se fait sur la rue normalisée ET le code postal.
-- Correction du rapport : jointure sur iris_evry.id_rue (et non IRIS_Paris.ID_Rue).
DROP TABLE IF EXISTS cible.consommation_iris_evry;
CREATE TABLE cible.consommation_iris_evry AS
WITH iris_evry AS (
    SELECT id_rue, id_ville, id_iris
    FROM s4.iris
    WHERE id_ville LIKE '91%'
)
SELECT i.id_iris,
    avg(c.nb_kw_jour * 365) AS conso_moyenne_annuelle
FROM iris_evry i
    JOIN s2.consommation c
        ON i.id_rue = lower(trim(c.nom_rue))
        AND i.id_ville = trim(c.code_postal)
GROUP BY i.id_iris;
