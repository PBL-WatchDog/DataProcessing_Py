import warnings
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.warnings import MissingPivotFunction

warnings.simplefilter("ignore", MissingPivotFunction)

source_bucket="Sensor_test"
dest_bucket="smarthome"

source_token = "RptXOiMCz2Fs9vV66Gz1Xnyptdy3J6kMMnPP89JcEgn8REXmExFw9w6EWjbbVoHpl7VoRsVnB6sdIKUJVUBYiA=="
dest_token = "1cDBU-BVSjJ0emb2KmZjgOhGNs3V1-cW60aqfMHoaeyndLVVdFfIo_Gp81OZn1iZ6gCHUvTjoi2rheflojizOg=="
source_url = "http://210.123.135.176:8086"
dest_url = "http://localhost:8086"
org = "Brighten"

# Source InfluxDB 연결 설정
source_client = influxdb_client.InfluxDBClient(url=source_url, token=source_token, org=org)
source_query_api = source_client.query_api()

# Destination InfluxDB 연결 설정
dest_client = influxdb_client.InfluxDBClient(url=dest_url, token=dest_token, org=org)
dest_write_api = dest_client.write_api(write_options=SYNCHRONOUS)

query = f'''
    from(bucket: "{source_bucket}")
        |> range(start: 0, stop: 2023-10-04T04:09:45.454Z)
'''

print("Source에서 데이터 조회 및 판다스 DataFrame 변환 시작")
# Source에서 데이터 조회 및 판다스 DataFrame 변환
result = source_query_api.query_data_frame(query)
print("Source에서 데이터 조회 및 판다스 DataFrame 변환 완료")

print(f"Destination에 데이터 쓰기 시작")
# Destination에 데이터 쓰기
for table in result:
    for index, row in table.iterrows():
        point = None
        if row.get("Device"):
            point = influxdb_client.Point(row["_measurement"]) \
                .tag("mac_address", row["mac_address"]) \
                .tag("Device", row["Device"]) \
                .field(row["_field"], row["_value"]) \
                .time(row["_time"])
        elif row.get("mac_address"):
            point = influxdb_client.Point(row["_measurement"]) \
                .tag("mac_address", row["mac_address"]) \
                .field(row["_field"], row["_value"]) \
                .time(row["_time"])
            
        if point:
            dest_write_api.write(bucket=dest_bucket, record=point)
print("Destination에 데이터 쓰기 완료")
# 클라이언트 종료
source_client.__del__()
dest_client.__del__()
