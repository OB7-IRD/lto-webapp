/* ============================================================
   ETAPE 1 : Déterminer l'océan pour chaque activité de pêche
   ------------------------------------------------------------
   On regarde la longitude de chaque position.
   - Si longitude >= 20 → Océan Indien (IND)
   - Si longitude < 20  → Atlantique (ATL)
============================================================ */

WITH activity_ocean AS (

    SELECT
        t.trip_id,

        CASE
            WHEN p.longitude >= 20 THEN 'IND'   -- Océan Indien
            WHEN p.longitude < 20 THEN 'ATL'    -- Océan Atlantique
            ELSE NULL                           -- Cas improbable
        END AS ocean

    FROM trip t
    JOIN fishing_activity fa ON fa.trip_trip_id = t.trip_id
    JOIN position p ON p.position_id = fa.position_fk
)


/* ============================================================
   ETAPE 2 : Déterminer l'océan global d'une marée (trip)
   ------------------------------------------------------------
   Une marée peut avoir plusieurs activités.
   On compte donc le nombre d'océans différents trouvés.
   - Si 1 seul océan → on garde cet océan
   - Si plusieurs → on indiquera 'MUL' pour Multiple
============================================================ */

, trip_ocean AS (

    SELECT
        trip_id,
        COUNT(DISTINCT ocean) AS ocean_count,  -- Nombre d'océans différents
        MIN(ocean) AS ocean                    -- Si un seul océan, MIN = cet océan
    FROM activity_ocean
    GROUP BY trip_id
)


/* ============================================================
   ETAPE 3 : Requête principale des marées
   ------------------------------------------------------------
   On récupère les infos du trip + les ports + le navire,
   et on ajoute l'océan calculé précédemment.
============================================================ */

SELECT
    t.trip_id AS trip_id,
    t.date_dep AS trip_start_date,
    t.date_rtp AS trip_end_date,
    t.master_name AS trip_captain_name,
    t.partial_landing AS trip_partial_landing,
    t.ers_trip_number AS trip_ers_id,

    -- Ports
    t.harbour_dep_fk AS trip_departure_harbour_id,
    dh.harbour_name AS trip_departure_harbour_name,
    dh.locode AS trip_departure_harbour_locode,
    t.harbour_rtp_fk AS trip_landing_harbour_id,
    lh.harbour_name AS trip_landing_harbour_name,
    lh.locode AS trip_landing_harbour_locode,

    -- Navire
    v.turbobat_number AS trip_vessel_turbobat_id,
    v.cfr_id AS trip_vessel_cfr_id,
    v.vessel_name AS trip_vessel_name,

    -- Nombre d'espèces présentes au départ
    COUNT(sp.specie_id) AS species_count_at_departure,

    /* ===================================================
       Calcul final de l'océan de la marée
       ---------------------------------------------------
       - Si un seul océan trouvé → on affiche cet océan
       - Si plusieurs → 'MUL'
       - Sinon → NULL
    =================================================== */

    CASE
        WHEN tocean.ocean_count = 1 THEN tocean.ocean
        WHEN tocean.ocean_count > 1 THEN 'MUL'
        ELSE NULL
    END AS trip_ocean

FROM public.trip t

-- Ports
INNER JOIN public.harbour dh ON t.harbour_dep_fk = dh.harbour_id
INNER JOIN public.harbour lh ON t.harbour_rtp_fk = lh.harbour_id

-- Navire
INNER JOIN public.vessel v ON t.turbobat_number = v.turbobat_number

-- Espèces au départ
LEFT JOIN adep da ON da.trip_trip_id = t.trip_id
LEFT JOIN specie sp ON sp.activitydeparturetoport_adep_id = da.adep_id

-- Océan calculé
LEFT JOIN trip_ocean tocean ON tocean.trip_id = t.trip_id

-- Filtre sur les dates
WHERE
    EXTRACT(YEAR FROM t.date_rtp) >= 2000
    AND t.date_rtp <= NOW() - INTERVAL '48 hours'

GROUP BY
    t.trip_id,
    t.date_dep,
    t.date_rtp,
    t.master_name,
    t.partial_landing,
    t.ers_trip_number,
    t.harbour_dep_fk,
    dh.harbour_name,
    dh.locode,
    t.harbour_rtp_fk,
    lh.harbour_name,
    lh.locode,
    v.turbobat_number,
    v.cfr_id,
    v.vessel_name,
    tocean.ocean,
    tocean.ocean_count

ORDER BY
    t.date_rtp DESC;
