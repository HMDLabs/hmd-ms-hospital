

drop view if exists device_hmd_lang_hospital;
create view device_hmd_lang_hospital as
    select
        id,
        content -> 'code' as code,
        content -> 'legal_status' as legal_status,
        content -> 'alternate_name' as alternate_name,
        content -> 'description' as description,
        content -> 'name' as name,
        content -> 'serial_number' as serial_number,
        created_at, updated_at
    from entity
    where is_deleted = false and name = 'hmd_lang_hospital.device';