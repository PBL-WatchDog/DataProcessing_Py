# import influxdb_client
import mysql.connector.pooling
import pandas as pd
from gateway_data_to_csv import gateway_data_to_csv
from door_data_to_csv import door_data_to_csv
from motion_data_to_csv import motion_data_to_csv
from plug_data_to_csv import plug_data_to_csv

# influxDB 설정
# token = "1cDBU-BVSjJ0emb2KmZjgOhGNs3V1-cW60aqfMHoaeyndLVVdFfIo_Gp81OZn1iZ6gCHUvTjoi2rheflojizOg=="
# org = "Brighten"
# url = "http://211.57.200.6:8086"
# bucket = "smarthome"

# client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
# query_api = client.query_api()

mac_addresses = [
    # 'W220_823510',
    # 'W220_823760',
    # 'W220_833660',
    # 'W220_8913B8',
    # 'W220_8917F0',
    # 'W220_891A04',
    # 'W220_892010',
    # 'W220_894FAC',
    # 'W220_895198',
    # 'W220_B83AC8',
    # 'W220_BADB10',
    # 'W220_BADBB8',
    # 'W220_BADC64',
    # 'W220_BE91D4',
    'W220_BE915C'
    ]

types = ['door', 'motion', 'plug']

# MySQL Pool 설정
dbconfig = {
    "host": "127.0.0.1",
    "user": "root",
    "password": 'willcam1190',
    "database": "smarthome",
    "port": 3306,
    "charset" : "utf8"
}

# Pool 생성
conn_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",
                                                        pool_size=10,
                                                        **dbconfig)

# sql 쿼리 실행 및 결과 반환
def sql_execute(query, params=None, dictionary=False):
    conn = conn_pool.get_connection()
    cursor = conn.cursor(dictionary=dictionary)

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    if cursor.with_rows:  # SELECT 문의 경우
        results = cursor.fetchall()
        results = results if results != [] else None    # select 문에 해당하는 행이 없으면 None으로 설정
    else:  # INSERT, UPDATE 또는 DELETE 문의 경우
        conn.commit()  # 쿼리를 커밋합니다.
        results = None  # 또는 영향받은 행의 수를 반환하려면 cursor.rowcount를 사용
    
    cursor.close()
    conn.close()

    return results

# gateway_id 값을 이용해 Device table에 등록된 모든 디바이스 id + type 반환
def get_deviceInfo_by_gatewayId(gateway_id, device_type=None, dictionary=None):
    if not device_type:
        params = (gateway_id, )
        sql = "select device_id, device_type from Device where gateway_id = %s"
    else:
        params = (gateway_id, device_type)
        sql = "select device_id, install_location from Device where gateway_id = %s and device_type = %s"
    return sql_execute(sql, params, dictionary or False)


for mac_address in mac_addresses:
    # 온습도(게이트웨이) 데이터
    print(mac_address)
    # gateway_data_to_csv(mac_address)

    # 센서 별 데이터
    for device_type in types:
        device_infos = get_deviceInfo_by_gatewayId(mac_address, device_type, False)
        device_id_list = list(dict(device_infos).keys())
        print('type:', device_type, ', list:', device_id_list)

        if device_type == 'motion':
            motion_data_to_csv(mac_address, device_type, device_id_list)

        # if device_type == 'door':
        #     door_data_to_csv(mac_address, device_type, device_id_list)
        # elif device_type == 'motion':
        #     motion_data_to_csv(mac_address, device_type, device_id_list)
        # elif device_type == 'plug':
        #     plug_data_to_csv(mac_address, device_type, device_id_list)
    print()
