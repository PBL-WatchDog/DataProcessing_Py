import paho.mqtt.client as mqtt
import ssl, json, random
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

#  (mqtt_client.connect가 잘 되면) 서버 연결이 잘되면 on_connect 실행 (이벤트가 발생하면 호출)
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

# 브로커에게 메시지가 도착하면 on_message 실행 (이벤트가 발생하면 호출)
def on_message(client, obj, msg):
    message = ""
    try:
        message = str(msg.payload.decode('utf-8'))
    except:
        message = msg
        print("error:", message)
        return

    data = json.loads(message)
    print("qos =", str(msg.qos))
    print("topic =", msg.topic)
    print(data)

    topic_split = msg.topic.split("/")
    if topic_split[2] == "SENSOR":
        if data.__contains__('SHTCX'):
            write_basic_data_tsdb(topic_split[1], data['SHTCX'])
        elif data.__contains__('ZbReceived'):
            write_sensor_data_tsdb(topic_split[1], data['ZbReceived'])
        else:
            print("이상한 데이터 형식")

        print()

def on_log(client, userdata, level, buf):
    print("log: ", buf)

# (mqtt_client.subscribe가 잘 되면) 구독(subscribe)을 완료하면
# on_subscrbie가 호출됨 (이벤트가 발생하면 호출됨)
def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribe complete : " + str(mid) + " " + str(granted_qos))


def write_basic_data_tsdb(gateway_model, gateway_data):
    point = (
                influxdb_client.Point("GatewayData")
                .tag("mac_address" , gateway_model)
                .field("temperature", gateway_data["Temperature"])
                .field("humidity", gateway_data["Humidity"])
                .field("dew_point", gateway_data["DewPoint"])
            )
    write_api.write(bucket=bucket, org=org, record=point)
    print(gateway_model + " basic data TSDB에 저장")

def write_sensor_data_tsdb(gateway_model, sensor_data):
    dump_property = ['Endpoint', 'LinkQuality', 'Device']

    for key, value in sensor_data.items():
        sensor_value = value

    point = influxdb_client.Point("SensorData").tag("mac_address" , gateway_model).tag("Device", sensor_value['Device'])
    for key in sensor_value:
        if key not in dump_property:
            if type(sensor_value[key]) == type(str()):
                point.field(key, str(sensor_value[key]))
            
    write_api.write(bucket=bucket, org=org, record=point)
    print(gateway_model + " sensor data TSDB에 저장")


#####################################################

token = "1cDBU-BVSjJ0emb2KmZjgOhGNs3V1-cW60aqfMHoaeyndLVVdFfIo_Gp81OZn1iZ6gCHUvTjoi2rheflojizOg=="
org = "Brighten"
url = "http://localhost:8086"
bucket="smarthome"
# new influxDB connection
# token = "1cDBU-BVSjJ0emb2KmZjgOhGNs3V1-cW60aqfMHoaeyndLVVdFfIo_Gp81OZn1iZ6gCHUvTjoi2rheflojizOg=="
# org = "Brighten"
# url = "http://localhost:8086"
# bucket="Sensor"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = write_client.write_api(write_options=SYNCHRONOUS)

#####################################################
random_number = random.randint(0, 100)

mqtt_client = mqtt.Client(f"client_{random_number}")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe
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
print(con_res)

# 여러 토픽을 구독 가능하다
mqtt_client.subscribe(sensor_topic, 0)
mqtt_client.subscribe(state_topic, 0)
mqtt_client.loop_forever()

