***Settings***
Library     OperatingSystem
Library     Collections
Library     String
Library   resources.HospitalClientLib.HospitalClientLib     ${HMD_INSTANCE_NAME}  ${HMD_REPO_NAME}  ${HMD_DID}  ${HMD_ENVIRONMENT}  ${HMD_REGION}  ${HMD_CUSTOMER_CODE}  ${HMD_ACCOUNT}
Variables   vars.py

Suite Setup     Setup Test Data


***Test Cases***
Add Device To Hospital
    [Documentation]     Calls /apiop/add_device/<id> custom operation
    [Template]      Call Add Device
    Test City Medical Center    1001    2022-06-15
    Saint Tester Hospital       5555    2022-08-07
    Saint Tester Hospital       2205    2022-12-16
    Test Clinic                 4423    2022-12-21


***Keywords***
Setup Test Data
    [Documentation]   Clears database and adds test data in ./data/
    Clear Db    ${gozer_instance_name}    ${pre_test_db_clear}   ${pre_test_dynamo_clear}
    Load Hospitals      ./data/hospitals.json
    Load Devices        ./data/devices.json

Call Add Device
    [Arguments]     ${hospital_name}    ${device_serial_number}     ${install_date}
    &{hospital_filter}=  Create Dictionary   attribute=name      operator=\=    value=${hospital_name}
    @{hospitals}=   Search An Entity   hmd_lang_hospital.hospital      ${hospital_filter}
    &{device_filter}=  Create Dictionary   attribute=serial_number      operator=\=   value=${device_serial_number}
    @{devices}=     Search An Entity    hmd_lang_hospital.device    ${device_filter}
    Add Device      ${hospitals[0].identifier}    ${devices[0].serialize()}       ${install_date}
    @{rels}=    Get To Relationships  ${devices[0]}     hmd_lang_hospital.hospital_owns_device
    Should Not Be Equal     ${rels[0].identifier}   ${NONE}
