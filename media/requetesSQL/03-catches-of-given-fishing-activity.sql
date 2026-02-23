SELECT
    c.id AS catch_id,
    sp.specie_id AS specie_id,
    --vessel.turbobat_number AS trip_vessel_turbobat_id,
    v.vessel_name  AS trip_vessel_name,
 	t.date_dep::date AS trip_start_date,
 	t.date_dep::time AS trip_start_time,
    t.date_rtp::date AS trip_end_date,
    t.date_rtp::time AS trip_end_time,
    fa.fishing_activity_id AS fa_id,
    fa.date::date AS fa_date,
    fa.date::time AS fa_time,
    fa.fa_operation AS fa_operation,
    fa.eez AS fa_eez,
    --p.latitude AS fa_latitude,
    --p.longitude AS fa_longitude,
    sp.nameofspecies AS specie_fao_id,
    sp.sizecategory AS specie_weight_category_id,
    sp.sizecomposition AS specie_weight_category_ers_id,
    sp.weightoffish/1000 AS specie_catchweight,
    sp.numberoffished AS specie_numberoffished,
    sp.numberoffishedtobelanded AS specie_numberoffishedtobelanded
FROM trip t
	INNER JOIN vessel v ON t.turbobat_number = v.turbobat_number
	INNER JOIN fishing_activity fa ON fa.trip_trip_id = t.trip_id
	INNER JOIN catch c ON c.fishingactivity_fishing_activity_id = fa.fishing_activity_id
	-- Positions normalement redondantes avec celle de la fishing_activity correspondante
	--INNER JOIN position p ON c.position_fk = p.position_id
	
	-- Semble être équivalent
	--INNER JOIN specie sp ON c.specie_fk = sp.specie_id
	INNER JOIN specie sp ON sp.capture_id = c.id
	
WHERE
	--t.trip_id IN (1134)
	fa.fishing_activity_id IN (%s)

ORDER BY
	v.vessel_name ASC,
	t.date_rtp DESC,
	fa.date DESC;