SELECT
	d.discard_id AS discard_id,
	t.trip_id AS trip_id,
    v.turbobat_number AS trip_vessel_turbobat_id,
    v.vessel_name AS trip_vessel_name,
 	t.date_dep::date AS trip_start_date,
 	t.date_dep::time AS trip_start_time,
    t.date_rtp::date AS trip_end_date,
    t.date_rtp::time AS trip_end_time,
    p.latitude AS discard_latitude,
    p.longitude AS discard_longitude,
    sp.nameofspecies AS species_fao_id,
    sp.nameofspecies AS specie_fao_id,
    sp.sizecategory AS specie_weight_category_id,
    sp.sizecomposition AS specie_weight_category_ers_id,
    sp.weightoffish/1000 AS specie_catchweight,
    sp.numberoffished AS specie_numberoffished,
    sp.numberoffishedtobelanded AS specie_numberoffishedtobelanded
FROM trip t
	INNER JOIN vessel v ON t.turbobat_number = v.turbobat_number
	INNER JOIN discard d ON d.trip_trip_id = t.trip_id
	INNER JOIN position p ON d.position_fk = p.position_id
	INNER JOIN specie sp ON sp.discard_discard_id = d.discard_id
	
WHERE
	--d.discard_id IN (1059)	--AND t.trip_id IN (1077)
	d.discard_id IN (%s) 		-- AND t.trip_id IN (1582)

ORDER BY
	v.vessel_name ASC,
	t.date_rtp DESC;