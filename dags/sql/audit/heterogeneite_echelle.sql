-- Audit d'hétérogénéité des échelles et granularités (Section 3.4)
-- Grandeur évaluée : Consommation.NB_KW_jour entre S1 (Paris) et S2 (Évry)
-- Métrique : Ratio_échelle = Moyenne(NB_KW_jour S2) / Moyenne(NB_KW_jour S1)
-- Interprétation :
--   - Ratio ≈ 1     : même unité dans les deux sources (ex. kW)
--   - Ratio ≈ 1000  : unités différentes (S2 en W, S1 en kW)
--   - Ratio ≈ 0,001 : unités différentes (S1 en W, S2 en kW)

WITH stats AS (
    SELECT
        (SELECT AVG(nb_kw_jour) FROM s1.consommation) AS moyenne_s1,
        (SELECT AVG(nb_kw_jour) FROM s2.consommation) AS moyenne_s2
)
SELECT
    ROUND(moyenne_s1, 4) AS moyenne_nb_kw_jour_s1,
    ROUND(moyenne_s2, 4) AS moyenne_nb_kw_jour_s2,
    ROUND(moyenne_s2 / NULLIF(moyenne_s1, 0), 4) AS ratio_echelle,
    CASE
        WHEN (moyenne_s2 / NULLIF(moyenne_s1, 0)) BETWEEN 0.5 AND 2.0
            THEN 'Même unité dans les deux sources (ratio ≈ 1)'
        WHEN (moyenne_s2 / NULLIF(moyenne_s1, 0)) >= 500
            THEN 'Unités différentes : S2 en W, S1 en kW (ratio ≈ 1000)'
        WHEN (moyenne_s2 / NULLIF(moyenne_s1, 0)) <= 0.002
            THEN 'Unités différentes : S1 en W, S2 en kW (ratio ≈ 0.001)'
        ELSE 'Écart atypique'
    END AS interpretation
FROM stats;
