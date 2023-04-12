

drop view if exists hospital_hmd_lang_hospital;
create view hospital_hmd_lang_hospital as
    select
        id,
        content -> 'name' as name,
        content -> 'address' as address,
        content -> 'opening_hours' as opening_hours,
        content -> 'geo' as geo,
        content -> 'logo' as logo,
        content -> 'telephone' as telephone,
        content -> 'legal_name' as legal_name,
        content -> 'lei_code' as lei_code,
        content -> 'number_of_employees' as number_of_employees,
        created_at, updated_at
    from entity
    where is_deleted = false and name = 'hmd_lang_hospital.hospital';