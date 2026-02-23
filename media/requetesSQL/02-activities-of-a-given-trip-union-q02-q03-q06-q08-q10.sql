
-- ------------------------------------------------------------------------
-- Target database : ers_prod on vmot-proto.ird.fr
--
-- Description : Returns all the activities of the given Trip id. This query is the union of
--				 4 base quesries:
--					- 02-departure-query
--					- 03-fishing-activities-query
--					- 06-discard-activities-of-given-trip
--					- 08-fd-activities query
--					- 10-end-activity-query
-- 				 Result set formatted to enable delivering table specific data
--
-- Author : P. CAUQUIL
-- Date : 2023-07-15
--
-- Updates : 2023-11-22 - Added ORDER BY (...) 	a_table ASC
-- Updates : 2025-11-15 - Added discard activities
-- ------------------------------------------------------------------------

-- Departure activity (adep table)
(SELECT
   	'adep' AS a_table,
   	da.adep_id AS a_id,
   	t.trip_id AS trip_id,
    v.vessel_name AS trip_vessel_name,
    dh.harbour_name AS trip_departure_port_name,
    dh.locode AS trip_departure_port_locode,
 	lh.harbour_name AS trip_landing_port_name,
 	lh.locode AS trip_landing_port_locode,
 	t.date_dep::date AS trip_start_date,
 	t.date_dep::time AS trip_start_time,
    t.date_rtp::date AS trip_end_date,
    t.date_rtp::time AS trip_end_time,
    da.date::date AS a_date,
    da.date::time AS a_time,
    -- From join with end_fishing table
    NULL::date AS fa_end_fishing_date,
    NULL::time AS fa_end_fishing_time,
    
    CASE
	    WHEN p.longitude >= 20 THEN 'IND'::text
	    WHEN p.longitude < 20 THEN 'ATL'::text
	    ELSE NULL::text
    END AS a_ocean,
    
    p.latitude AS a_latitude,
    p.longitude AS a_longitude,
    dah.harbour_name AS a_port_name,
 	dah.locode AS a_port_locode,
    da.degree_current AS a_current_direction,
    da.speed_current AS a_current_speed,
    da.degree_wind AS a_wind_direction,
    da.speed_wind AS a_wind_speed,
    da.sea_state AS a_sea_state,
    da.sea_surface_temperature AS a_sst,
    da.school_size_information/1000 AS a_school_size,
    NULL::boolean AS a_positive_set,
    da.misc_problems AS a_misc_problems,
    NULL::text AS a_operation,
    NULL::text a_eez,
    -- For compatibility with fishing_activity
    NULL::text AS gear_type,
    NULL::text AS gear_dimensions,
    NULL::integer AS gear_fishing_depth,
    NULL::integer AS gear_mesh_size,
    NULL::integer AS gear_total_length,
    -- For compatibility with fad_activity
    NULL::text AS fad_type,
    NULL::boolean AS fad_has_buoy,
    NULL::text AS fad_comment,
    -- Buoy
    NULL::text AS buoy_type,
    NULL::text AS buoy_identifier,
    NULL::text AS buoy_comment,
    -- Fishing contexts
    NULL::text AS fishing_contexts
    
FROM trip t
	INNER JOIN vessel v ON t.turbobat_number = v.turbobat_number
	INNER JOIN harbour dh ON t.harbour_dep_fk = dh.harbour_id
	INNER JOIN harbour lh ON t.harbour_rtp_fk = lh.harbour_id
	INNER JOIN adep da ON da.trip_trip_id = t.trip_id
	INNER JOIN harbour dah ON da.harbour_id = dah.harbour_id
	LEFT OUTER JOIN position p ON da.position_fk = p.position_id
	
WHERE
	t.trip_id IN (%s)
	
ORDER BY
	v.vessel_name ASC,
	t.date_rtp ASC,
	da.date ASC
)

UNION

-- Fishing activities (fishing_activity table)
(SELECT
	'fishing_activity' AS a_table,
   	fa.fishing_activity_id AS a_id,
   	t.trip_id AS trip_id,
    v.vessel_name AS trip_vessel_name,
    dh.harbour_name AS trip_departure_port_name,
    dh.locode AS trip_departure_port_locode,
 	lh.harbour_name AS trip_landing_port_name,
 	lh.locode AS trip_landing_port_locode,
 	t.date_dep::date AS trip_start_date,
 	t.date_dep::time AS trip_start_time,
    t.date_rtp::date AS trip_end_date,
    t.date_rtp::time AS trip_end_time,
    fa.date::date AS a_date,
    fa.date::time AS a_time,
    -- From join with end_fishing table
    ef.date_eof::date AS fa_end_fishing_date,
    ef.date_eof::time AS fa_end_fishing_time,
    
    CASE
	    WHEN p.longitude >= 20 THEN 'IND'::text
	    WHEN p.longitude < 20 THEN 'ATL'::text
	    ELSE NULL::text
    END AS a_ocean,
    
    p.latitude AS a_latitude,
    p.longitude AS a_longitude,
    -- For compatibility with departure_activity (adep) and end_activity (artp)
    NULL::text AS a_port_name,
 	NULL::text AS a_port_locode,
    fa.degree_current AS a_current_direction,
    fa.speed_current AS a_current_speed,
    fa.degree_wind AS a_wind_direction,
    fa.speed_wind AS a_wind_speed,
    fa.sea_state AS a_sea_state,
    fa.sea_surface_temperature AS a_sst,
    fa.school_size_information/1000 AS a_school_size,
    fa.succesful AS a_positive_set,
    fa.misc_problems AS a_misc_problems,
    fa.fa_operation AS a_operation,
    fa.eez AS a_eez,
    -- Gear
    g.type AS gear_type,
    g.dimensions AS gear_dimensions,
    g.fishing_depths AS gear_fishing_depth,
    g.mesh_size AS gear_mesh_size,
    g.total_length AS gear_total_length,
    -- For compatibility with fad_activity
    NULL::text AS fad_type,
    NULL::boolean AS fad_has_buoy,
    NULL::text AS fad_comment,
    -- Buoy
    NULL::text AS buoy_type,
    NULL::text AS buoy_identifier,
    NULL::text AS buoy_comment,
    -- Fishing contexts
    string_agg(concat('(type:',fc.type,',is_shot:',fc.is_shot,')'), ';') AS fishing_contexts
	    
FROM trip t
	INNER JOIN vessel v ON (t.turbobat_number = v.turbobat_number)
	INNER JOIN harbour dh ON (t.harbour_dep_fk = dh.harbour_id)
	INNER JOIN harbour lh ON (t.harbour_rtp_fk = lh.harbour_id)
	INNER JOIN fishing_activity fa ON (fa.trip_trip_id = t.trip_id)
	INNER JOIN position p ON (fa.position_fk = p.position_id)
	INNER JOIN gear g ON (fa.gear_id_fk = g.gear_id)
	LEFT OUTER JOIN end_fishing ef ON (ef.fishing_activity_id = fa.fishing_activity_id)
	LEFT OUTER JOIN fishing_context fc ON (fc.fishingactivity_fishing_activity_id = fa.fishing_activity_id)
	
WHERE
	t.trip_id IN (%s)
	
GROUP BY
	a_id,
   	trip_id,
    trip_vessel_name,
    trip_departure_port_name,
    trip_departure_port_locode,
 	trip_landing_port_name,
 	trip_landing_port_locode,
 	t.date_dep,
    t.date_rtp,
    fa.date,
    ef.date_eof,
    a_ocean,
    a_latitude,
    a_longitude,
    a_port_name,
 	a_port_locode,
    a_current_direction,
    a_current_speed,
    a_wind_direction,
    a_wind_speed,
    a_sea_state,
    a_sst,
    a_school_size,
    a_positive_set,
    a_misc_problems,
    a_operation,
    a_eez,
    gear_type,
    gear_dimensions,
    gear_fishing_depth,
    gear_mesh_size,
    gear_total_length,
    fad_type,
    fad_has_buoy,
    fad_comment,
    buoy_type,
    buoy_identifier,
    buoy_comment

ORDER BY
	v.vessel_name ASC,
	t.date_rtp ASC,
	fa.date ASC
)

UNION

-- Discard activities
(SELECT DISTINCT
    'discard' AS a_table,
   	d.discard_id AS a_id,
   	t.trip_id AS trip_id,
    v.vessel_name AS trip_vessel_name,
    dh.harbour_name AS trip_departure_port_name,
    dh.locode AS trip_departure_port_locode,
 	lh.harbour_name AS trip_landing_port_name,
 	lh.locode AS trip_landing_port_locode,
 	t.date_dep::date AS trip_start_date,
 	t.date_dep::time AS trip_start_time,
    t.date_rtp::date AS trip_end_date,
    t.date_rtp::time AS trip_end_time,
    d.date::date AS a_date,
    d.date::time AS a_time,
    -- From join with end_fishing table
    NULL::date AS fa_end_fishing_date,
    NULL::time AS fa_end_fishing_time,
    
    CASE
	    WHEN p.longitude >= 20 THEN 'IND'::text
	    WHEN p.longitude < 20 THEN 'ATL'::text
	    ELSE NULL::text
    END AS a_ocean,
    
    p.latitude AS a_latitude,
    p.longitude AS a_longitude,
    -- For compatibility with departure_activity (adep) and end_activity (artp)
    NULL::text AS a_port_name,
 	NULL::text AS a_port_locode,
    NULL::text AS a_current_direction,
    NULL::numeric AS a_current_speed,
    NULL::text AS a_wind_direction,
    NULL::numeric AS a_wind_speed,
    NULL::text AS a_sea_state,
    NULL::numeric AS a_sst,
    NULL::numeric AS a_school_size,
    NULL::bool AS a_positive_set,
    NULL::text AS a_misc_problems,
    NULL::text AS a_operation,
    NULL::text AS a_eez,
    -- Gear
    NULL::text AS gear_type,
    NULL::text AS gear_dimensions,
    NULL::integer AS gear_fishing_depth,
    NULL::integer AS gear_mesh_size,
    NULL::integer AS gear_total_length,
    -- For compatibility with fad_activity
    NULL::text AS fad_type,
    NULL::boolean AS fad_has_buoy,
    NULL::text AS fad_comment,
    -- Buoy
    NULL::text AS buoy_type,
    NULL::text AS buoy_identifier,
    NULL::text AS buoy_comment,
    -- Fishing contexts
    NULL::text AS fishing_contexts

FROM trip t
	INNER JOIN vessel v ON (t.turbobat_number = v.turbobat_number)
	INNER JOIN harbour dh ON (t.harbour_dep_fk = dh.harbour_id)
	INNER JOIN harbour lh ON (t.harbour_rtp_fk = lh.harbour_id)
	INNER JOIN discard d ON (d.trip_trip_id = t.trip_id)
	INNER JOIN position p ON (d.position_fk = p.position_id)
	
WHERE
	t.trip_id IN (%s)

ORDER BY
	d.discard_id ASC,
	v.vessel_name ASC,
	t.date_rtp::date DESC,
	t.date_rtp::time DESC
)
	
UNION

-- FAD activities (fad_activity table)
(SELECT
   	'fad_activity' AS a_table,
   	fda.fad_activity_id AS a_id,
   	t.trip_id AS trip_id,
    v.vessel_name AS trip_vessel_name,
    dh.harbour_name AS trip_departure_port_name,
    dh.locode AS trip_departure_port_locode,
 	lh.harbour_name AS trip_landing_port_name,
 	lh.locode AS trip_landing_port_locode,
 	t.date_dep::date AS trip_start_date,
 	t.date_dep::time AS trip_start_time,
    t.date_rtp::date AS trip_end_date,
    t.date_rtp::time AS trip_end_time,
    fda.date::date AS a_date,
    fda.date::time AS a_time,
    -- From join with end_fishing table
    NULL::date AS fa_end_fishing_date,
    NULL::time AS fa_end_fishing_time,
    
    CASE
	    WHEN p.longitude >= 20 THEN 'IND'::text
	    WHEN p.longitude < 20 THEN 'ATL'::text
	    ELSE NULL::text
    END AS a_ocean,
    
    p.latitude AS a_latitude,
    p.longitude AS a_longitude,
    -- For compatibility with departure_activity (adep) and end_activity (artp)
    NULL::text AS a_port_name,
 	NULL::text AS a_port_locode,
    fda.degreeofcurrent AS a_current_direction,
    fda.speedofcurrent AS a_current_speed,
    fda.degreeofwind AS a_wind_direction,
    fda.speedofwind AS a_wind_speed,
    fda.seastate AS a_sea_state,
    fda.seasurfacetemperature AS a_sst,
    fda.schoolsizeinfomartion/1000 AS a_school_size,
    NULL::boolean AS a_positive_set,
    fda.miscproblems AS a_misc_problems,
    fda.operation AS a_operation,
    fda.economiczone AS a_eez,
    -- For compatibility with fishing_activity
    NULL::text AS gear_type,
    NULL::text AS gear_dimensions,
    NULL::integer AS gear_fishing_depth,
    NULL::integer AS gear_mesh_size,
    NULL::integer AS gear_total_length,
    -- FAD
    fd.type AS fad_type,
    fd.has_buoy AS fad_has_buoy,
    fd.comment AS fad_comment,
    -- Buoy
    b.type AS buoy_type,
    b.identifier AS buoy_identifier,
    b.comment AS buoy_comment,
    -- Fishing contexts
    string_agg(concat('(type:',fc.type,',is_shot:',fc.is_shot,')'), ';') AS fishing_contexts
    
FROM trip t
	INNER JOIN vessel v ON t.turbobat_number = v.turbobat_number
	INNER JOIN harbour dh ON t.harbour_dep_fk = dh.harbour_id
	INNER JOIN harbour lh ON t.harbour_rtp_fk = lh.harbour_id
	INNER JOIN fad_activity fda ON fda.trip_trip_id = t.trip_id
	INNER JOIN position p ON fda.position_fk = p.position_id
	INNER JOIN fad fd ON fda.fad_fk = fd.fad_id
	LEFT OUTER JOIN buoy b ON b.fad_fad_id = fd.fad_id
	LEFT OUTER JOIN fishing_context fc ON fc.fishingactivity_fishing_activity_id = fda.fad_activity_id
	
WHERE
	t.trip_id IN (%s)
	
GROUP BY
	a_id,
   	trip_id,
    trip_vessel_name,
    trip_departure_port_name,
    trip_departure_port_locode,
 	trip_landing_port_name,
 	trip_landing_port_locode,
 	t.date_dep,
    t.date_rtp,
    fda.date,
    a_ocean,
    a_latitude,
    a_longitude,
    a_port_name,
 	a_port_locode,
    a_current_direction,
    a_current_speed,
    a_wind_direction,
    a_wind_speed,
    a_sea_state,
    a_sst,
    a_school_size,
    a_positive_set,
    a_misc_problems,
    a_operation,
    a_eez,
    gear_type,
    gear_dimensions,
    gear_fishing_depth,
    gear_mesh_size,
    gear_total_length,
    fad_type,
    fad_has_buoy,
    fad_comment,
    buoy_type,
    buoy_identifier,
    buoy_comment

ORDER BY
	v.vessel_name ASC,
	t.date_rtp ASC,
	fda.date ASC
)

UNION

-- Come back at port
(SELECT
   	'artp' AS a_table,
   	ea.artp_id AS a_id,
   	t.trip_id AS trip_id,
    v.vessel_name AS trip_vessel_name,
    dh.harbour_name AS trip_departure_port_name,
    dh.locode AS trip_departure_port_locode,
 	lh.harbour_name AS trip_landing_port_name,
 	lh.locode AS trip_landing_port_locode,
 	t.date_dep::date AS trip_start_date,
 	t.date_dep::time AS trip_start_time,
    t.date_rtp::date AS trip_end_date,
    t.date_rtp::time AS trip_end_time,
    ea.date::date AS a_date,
    ea.date::time AS a_time,
    -- From join with end_fishing table
    NULL::date AS fa_end_fishing_date,
    NULL::time AS fa_end_fishing_time,
    
    CASE
	    WHEN p.longitude >= 20 THEN 'IND'::text
	    WHEN p.longitude < 20 THEN 'ATL'::text
	    ELSE NULL::text
    END AS a_ocean,
    
    p.latitude AS a_latitude,
    p.longitude AS a_longitude,
    dah.harbour_name AS a_port_name,
 	dah.locode AS a_port_locode,
    ea.degree_current AS a_current_direction,
    ea.speed_current AS a_current_speed,
    ea.degree_wind AS a_wind_direction,
    ea.speed_wind AS a_wind_speed,
    ea.sea_state AS a_sea_state,
    ea.sea_surface_temperature AS a_sst,
    ea.school_size_information/1000 AS a_school_size,
    NULL::boolean AS a_positive_set,
    ea.misc_problems AS a_misc_problems,
    NULL::text AS a_operation,
    NULL::text a_eez,
    -- For compatibility with fishing_activity
    NULL::text AS gear_type,
    NULL::text AS gear_dimensions,
    NULL::integer AS gear_fishing_depth,
    NULL::integer AS gear_mesh_size,
    NULL::integer AS gear_total_length,
    -- For compatibility with fad_activity
    NULL::text AS fad_type,
    NULL::boolean AS fad_has_buoy,
    NULL::text AS fad_comment,
    -- Buoy
    NULL::text AS buoy_type,
    NULL::text AS buoy_identifier,
    NULL::text AS buoy_comment,
    -- Fishing contexts
    NULL::text AS fishing_contexts
    
FROM trip t
	INNER JOIN vessel v ON t.turbobat_number = v.turbobat_number
	INNER JOIN harbour dh ON t.harbour_dep_fk = dh.harbour_id
	INNER JOIN harbour lh ON t.harbour_rtp_fk = lh.harbour_id
	INNER JOIN artp ea ON ea.trip_trip_id = t.trip_id
	INNER JOIN harbour dah ON ea.harbour_id = dah.harbour_id
	LEFT OUTER JOIN position p ON ea.position_fk = p.position_id
	
WHERE
	t.trip_id IN (%s)
	
ORDER BY
	v.vessel_name ASC,
	t.date_rtp ASC,
	ea.date ASC
)

ORDER BY
	trip_vessel_name ASC,
	trip_end_date ASC,
	trip_end_time ASC,
	a_date ASC,
	a_time ASC,
	a_table ASC