import paho.mqtt.client as mqtt

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import mysql.connector.pooling

from datetime import datetime
import ssl, json, random

#  (mqtt_client.connect가 잘 되면) 서버 연결이 잘되면 on_connect 실행 (이벤트가 발생하면 호출)
def on_connect(client, userdata, flags, rc):
    print(f'flags: {flags}')
    print("rc: " + str(rc))

# 브로커에게 메시지가 도착하면 on_message 실행 (이벤트가 발생하면 호출)
def on_message(client, userdata, msg):
    try:
        data = json.loads(str(msg.payload.decode('utf-8')))
    except Exception as es:
        print(f"error: {es}")
        print(f'msg: {msg}')
        return

    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]')
    print("topic =", msg.topic)
    print(data)

    topic_split = msg.topic.split("/")
    gateway_model = topic_split[1]
    if topic_split[2] == "SENSOR":
        if data.__contains__('SHTCX'):
            write_basic_data_tsdb(topic_split[1], data['SHTCX'])
        elif data.__contains__('ZbReceived'):
            # 필요한 데이터만 딕셔너리에서 추출
            data = data['ZbReceived']
            for key, value in data.items():
                sensor_value = value

            if sensor_value.__contains__('ModelId'):    # ModelId -> 디바이스가 게이트웨이로 등록된 상황
                # mysql table 등록 대기 디바이스 저장
                print(f'------{gateway_model} Gateway -> {sensor_value["Device"]} Device 대기 등록------')
                register_device(sensor_value['Device'], gateway_model, get_device_type_by_ModelId(sensor_value["ModelId"]))
                
            write_sensor_data_tsdb(gateway_model, sensor_value)
        else:
            print("------Invalid Data Type------")

        print()

def on_log(client, userdata, level, buf):
    print(f'level: {level}')
    print(f'buf: {buf}')

# (mqtt_client.subscribe가 잘 되면) 구독(subscribe)을 완료하면
# on_subscrbie가 호출됨 (이벤트가 발생하면 호출됨)
def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribe complete : " + str(mid) + " " + str(granted_qos))

##################DB function######################

def write_basic_data_tsdb(gateway_model, gateway_data):
    point = (
                influxdb_client.Point("GatewayData")
                .tag("mac_address" , gateway_model)
                .field("temperature", gateway_data["Temperature"])
                .field("humidity", gateway_data["Humidity"])
                .field("dew_point", gateway_data["DewPoint"])
            )
    write_api.write(bucket=bucket, org=org, record=point)
    # print(gateway_model + " basic data TSDB에 저장")

def write_sensor_data_tsdb(gateway_model, sensor_value):
    dump_property = set(['Endpoint', 'LinkQuality', 'Device', 'AppVersion']) # AppVersion propery 추가 + set으로 자료형 변경
    type_set = set([type(str()), type(int()), type(float())])

    point = influxdb_client.Point("SensorData").tag("mac_address" , gateway_model).tag("Device", sensor_value['Device'])
    for key, value in sensor_value.items():     # .items() 메소드로 변경
        if key not in dump_property:
            if type(value) in type_set:     # type list -> set 변경
                point.field(key, str(value))
            
    write_api.write(bucket=bucket, org=org, record=point)
    # print(gateway_model + " sensor data TSDB에 저장")

def register_device(device_id, gateway_id, modelId, dictionary=False):
    conn = conn_pool.get_connection()
    cursor = conn.cursor(dictionary=dictionary)

    sql = "insert into PendingDevice(device_id, gateway_id, device_type) Values(%s, %s, %s)"
    params = (device_id, gateway_id, modelId)
    cursor.execute(sql, params)
   
    conn.commit()  # 쿼리를 커밋합니다.
    cursor.close()
    conn.close()

# modelId를 통해 디바이스 종류 찾기
def get_device_type_by_ModelId(ModelID):
    device_type_dic = {
        "RH3001": "door",
        "lumi.magnet.agl02": "door",
        "multi": "door",
        "TS004F" : "swtich",
        "RH3040": "motion",
        "TS0202": "motion",
        "lumi.motion.agl02": "motion",
        "TS0207": "leak",
        "TS0601": "smoke",
        "lumi.plug.maeu01": "plug",     
    }#"illumination": "lumi.motion.agl02"
    return device_type_dic[ModelID]

##################new influxDB connection##################

token = "1cDBU-BVSjJ0emb2KmZjgOhGNs3V1-cW60aqfMHoaeyndLVVdFfIo_Gp81OZn1iZ6gCHUvTjoi2rheflojizOg=="
org = "Brighten"
url = "http://localhost:8086"
bucket="smarthome"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = write_client.write_api(write_options=SYNCHRONOUS)

###################Connection Pool 설정#######################

dbconfig = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "willcam1190",
    "database": "smarthome",
    "port": 3306,
    "charset" : "utf8"
}

# Pool 생성
conn_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",
                                                        pool_size=10,
                                                        **dbconfig)

#####################---MAIN---#######################

random_number = random.randint(0, 100)

mqtt_client = mqtt.Client(f"client_{random_number}")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe
# mqtt_client.on_log = on_log
# mqtt_client.on_publish = on_publish

broker_address = "smarthome.brighten.co.kr"
port = 8883
username = "smarthome.brighten.co.kr"
password = "smarthome1357!@"
sensor_topic = "tele/+/SENSOR"
state_topic = "tele/+/STATE"

mqtt_client.tls_set("/home/smarthome/cert/ca.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
mqtt_client.tls_insecure_set(True)

mqtt_client.username_pw_set(username, password)
con_res = mqtt_client.connect(broker_address, port)
print("------------------------------------------------------------")
print(f'con_res: {con_res}')

# 여러 토픽을 구독 가능하다
mqtt_client.subscribe(sensor_topic, 0)
mqtt_client.subscribe(state_topic, 0)
mqtt_client.loop_forever()

