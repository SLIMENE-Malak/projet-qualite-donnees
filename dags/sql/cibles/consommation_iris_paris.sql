-- Cible : Consommation_IRIS_Paris (ID_IRIS, Conso_moyenne_annuelle)
-- Dans s4.iris, id_ville contient le code postal (75001...) et id_rue le nom de rue
-- en minuscules : la jointure se fait sur la rue normalisée ET le code postal,
-- sinon une rue présente dans deux arrondissements serait comptée deux fois.
DROP TABLE IF EXISTS cible.consommation_iris_paris;
CREATE TABLE cible.consommation_iris_paris AS
WITH iris_paris AS (
    SELECT id_rue, id_ville, id_iris
    FROM s4.iris
    WHERE id_ville LIKE '75%'
)
SELECT i.id_iris,
    avg(c.nb_kw_jour * 365) AS conso_moyenne_annuelle
FROM iris_paris i
    JOIN s1.consommation c
        ON i.id_rue = lower(trim(c.nom_rue))
        AND i.id_ville = trim(c.code_postal)
GROUP BY i.id_iris;
