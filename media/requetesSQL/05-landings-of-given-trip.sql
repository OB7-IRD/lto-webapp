SELECT
	l.landing_id AS landing_id,
	t.trip_id AS trip_id,
    v.vessel_name AS trip_vessel_name,
 	t.date_dep::date AS trip_start_date,
 	t.date_dep::time AS trip_start_time,
    t.date_rtp::date AS trip_end_date,
    t.date_rtp::time AS trip_end_time,
    sp.nameofspecies AS specie_fao_id,
    sp.sizecategory AS specie_weight_category_id,
    sp.sizecomposition AS specie_weight_category_ers_id,
    sp.weightoffish/1000 AS specie_catchweight,
    sp.numberoffished AS specie_numberoffished,
    sp.numberoffishedtobelanded AS specie_numberoffishedtobelanded
FROM trip t
	INNER JOIN vessel v ON t.turbobat_number = v.turbobat_number
	INNER JOIN landing l ON l.trip_trip_id = t.trip_id
	INNER JOIN specie sp ON sp.landing_landing_id = l.landing_id
	
WHERE
	--t.trip_id IN (1582)
	t.trip_id IN (%s)

ORDER BY
	v.vessel_name ASC,
	t.date_rtp DESC;