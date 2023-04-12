import json
from typing import Dict, List
from hmd_lib_robot_shared.basic_client_robot_lib import BasicClientLib
from hmd_lang_hospital.hospital import Hospital
from hmd_lang_hospital.device import Device
from hmd_lang_hospital.hospital_owns_device import HospitalOwnsDevice
import psycopg2
import psycopg2.extras
from robot.api.deco import library, keyword
from robot.api import Failure
from hmd_cli_tools.hmd_cli_tools import get_session
from hmd_cli_tools.cdktf_tools import DeploymentConfig
import yaml


@library
class HospitalClientLib(BasicClientLib):
    def __init__(self, instance_name, repo_name, deployment_id, environment, hmd_region, customer_code, account_number=None, okta_secret_name=None):
        super().__init__(instance_name, repo_name, deployment_id, environment, hmd_region, customer_code, account_number, okta_secret_name)
        
        with open("instance_configuration.yaml", "r") as fl:
            instance_config = yaml.safe_load(fl)

        dp_config = DeploymentConfig(instance_config)

        self.dp_config = dp_config


    def clear_dynamo_table(self, dynamo_table, dynamo_url):
        session = get_session()
        dynamo_client = session.client("dynamodb", endpoint_url=dynamo_url)
        try:
            results = dynamo_client.scan(TableName=dynamo_table)
            for item in results["Items"]:
                dynamo_client.delete_item(
                    TableName=dynamo_table,
                    Key={
                        "identifier": {"S": item["identifier"]["S"]},
                        "version": {"S": item["version"]["S"]},
                    },
                )
        except dynamo_client.exceptions.ResourceNotFoundException:
            # don't fail if the table doesn't exist
            pass

    @keyword
    def clear_db(self, gozer_instance_name: str, pre_test_db_clear: Dict[str, List], dynamo_tables: List[str] = None):
        if self.environment == 'local':
            conn = psycopg2.connect(
                f"dbname={self.instance_name} host=db user={self.instance_name} password={self.instance_name}",
                cursor_factory=psycopg2.extras.DictCursor,
            )
            cur = conn.cursor()
            cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('entity',))
            if cur.fetchone()[0]:
                cur.execute("DELETE FROM entity WHERE 1=1")
            cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('relationship',))
            if cur.fetchone()[0]:
                cur.execute("DELETE FROM relationship WHERE 1=1")

            conn.commit()
            conn.close()

            config = self.dp_config.get("service_config", {}).get("hmd_db_engines", {}).get("dynamo", None)
            if config is None:
                return
            
            config = config.get("engine_config", {})
            table_name = config.get("dynamo_table", '')
            dynamo_url = config.get("dynamo_url")

            if dynamo_url is None:
                return
            
            self.clear_dynamo_table(table_name, dynamo_url)
            return
        
        return super().clear_service_db(gozer_instance_name=gozer_instance_name, pre_test_db_clear=pre_test_db_clear, dynamo_tables=dynamo_tables)

    @keyword
    def load_hospitals(self, data_file: str):
        with open(data_file, 'r') as df:
            hospital_data = json.load(df)

        for hospital in hospital_data:
            self.upsert_an_entity(Hospital(**hospital))

    @keyword
    def load_devices(self, data_file: str):
        with open(data_file, 'r') as df:
            device_data = json.load(df)

        for device in device_data:
            self.upsert_an_entity(Device(**device))

    @keyword
    def add_device(self, hospital_id: str, device_data: Dict, install_date: str):

        resp = self.rs._get_client_for_type(HospitalOwnsDevice.get_namespace_name()).invoke_custom_operation(f'/add_device/{hospital_id}', {
                "installation_date": install_date,
                "device": device_data
            }, "PUT")
        if 'Error Message' in resp:
            raise Failure(f"Calling add_device failed: {resp['Error Message']}")
        return resp

