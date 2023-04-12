from dateutil.parser import isoparse
from hmd_graphql.hmd_graphql import get_db_engines, get_first_db_engine
from hmd_graphql_client.hmd_db_engine_client import DbEngineClient

from hmd_lang_hospital.hmd_lang_hospital_client import (
    HmdLangHospitalClient,
    Device,
    HospitalOwnsDevice,
)


def setup(service):
    @service.operation(
        rest_path="/apiop/add_device/<args_id>",
        rest_methods=["PUT"],
        args={"id": "id", "payload": "json"},
    )
    def add_device(evt, ctx):
        """Adds a hmd_lang_hospital.device to a hmd_lang_hospital.hospital view the hospital_owns_device Relationship.
        Accepts a hospital identifier in the URL, and a device object in the body.
        """
        args = evt["args"]
        db_client = get_first_db_engine(evt, ctx)

        hospital_nid = args.get("id")

        if hospital_nid is None:
            raise Exception("Missing Hospital Identifier in URL")

        client = HmdLangHospitalClient(
            DbEngineClient(db_engine=db_client, loader=ctx["loader"])
        )

        hospital = client.get_hospital_hmd_lang_hospital(hospital_nid)

        if hospital is None:
            raise Exception(f"Cannot find Hospital: {hospital_nid}")

        device_data = args.get("payload", {}).get("device")

        if device_data is None:
            raise Exception("Missing device data in payload")

        device = Device.deserialize(Device, device_data)

        existing_devices = client.search_device_hmd_lang_hospital(
            {
                "attribute": "serial_number",
                "operator": "=",
                "value": device.serial_number,
            }
        )

        if len(existing_devices) > 1:
            raise Exception(
                f"Cannot find unique device with serial number: {device.serial_number}"
            )

        if len(existing_devices) == 1:
            device.identifier = existing_devices[0].identifier

        device = client.upsert_device_hmd_lang_hospital(device)

        rel = client.upsert_hospital_owns_device_hmd_lang_hospital(
            HospitalOwnsDevice(
                ref_from=hospital.identifier,
                ref_to=device.identifier,
                installation_date=isoparse(
                    args.get("payload", {}).get("installation_date")
                ),
            )
        )

        return rel.serialize()
