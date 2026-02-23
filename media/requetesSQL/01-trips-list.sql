-- ------------------------------------------------------------------------
-- Target database : ers_prod on vmot-proto.ird.fr
--
-- Description : Returns the list of trips available in the database
--
-- Author : P. CAUQUIL
-- Date : 2023-07-15
--
-- Updates : 2023-11-22 - Added vessel name
--						  Added filter to limit results to trips with ending date at now() - 48 hours
-- ------------------------------------------------------------------------

SELECT
	t.trip_id AS trip_id,
	t.date_dep AS trip_start_date,
	t.date_rtp AS trip_end_date,
	t.master_name AS trip_captain_name,
	t.partial_landing AS trip_partial_landing,
	t.ers_trip_number AS trip_ers_id,
	t.harbour_dep_fk AS trip_departure_harbour_id,
	dh.harbour_name AS trip_departure_harbour_name,
	dh.locode AS trip_departure_harbour_locode,
	t.harbour_rtp_fk AS trip_landing_harbour_id,
	lh.harbour_name AS trip_landing_harbour_name,
	lh.locode AS trip_landing_harbour_locode,
	v.turbobat_number AS trip_vessel_turbobat_id,
	v.cfr_id AS trip_vessel_cfr_id,
	v.vessel_name AS trip_vessel_name,
	-- If > 0, well are not empty at departure
	count(sp.specie_id) AS species_count_at_departure
	
FROM
	public.trip t
	INNER JOIN public.harbour dh ON (t.harbour_dep_fk = dh.harbour_id)
	INNER JOIN public.harbour lh ON (t.harbour_rtp_fk = lh.harbour_id)
	INNER JOIN public.vessel v ON (t.turbobat_number = v.turbobat_number)
	-- Supposed to provided species present onboard at departure, but doto always absent
	LEFT OUTER JOIN adep da ON (da.trip_trip_id = t.trip_id)
	LEFT OUTER JOIN specie sp ON (sp.activitydeparturetoport_adep_id = da.adep_id)
	
WHERE
	extract(year from date_rtp) >= 2000
	AND t.date_rtp <= now() - interval '48 hours'
	
GROUP BY
	trip_id,
	trip_start_date,
	trip_end_date,
	trip_captain_name,
	trip_partial_landing,
	trip_ers_id,
	trip_departure_harbour_id,
	trip_departure_harbour_name,
	trip_departure_harbour_locode,
	trip_landing_harbour_id,
	trip_landing_harbour_name,
	trip_landing_harbour_locode,
	trip_vessel_turbobat_id,
	trip_vessel_cfr_id,
	trip_vessel_name

ORDER BY
	t.date_rtp DESC;