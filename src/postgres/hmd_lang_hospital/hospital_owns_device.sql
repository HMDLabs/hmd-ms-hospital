

drop view if exists hospital_owns_device_hmd_lang_hospital;
create view hospital_owns_device_hmd_lang_hospital as
    select
        id,
        content -> 'installation_date' as installation_date,
        from_id,
        to_id,
        created_at, updated_at
    from relationship
    where is_deleted = false and name = 'hmd_lang_hospital.hospital_owns_device';