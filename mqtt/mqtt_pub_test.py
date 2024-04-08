import paho.mqtt.client as mqtt
import ssl


# (mqtt_client.publish가 잘 되면) 메시지를 publish하면 on_publish실행 (이벤트가 발생하면 호출)
def on_publish(client, obj, mid):
    # 용도 : publish를 보내고 난 후 처리를 하고 싶을 때
    # 사실 이 콜백함수는 잘 쓰진 않는다.
    print("mid: " + str(mid))


# 브로커 정보 입력
broker_address = "smarthome.brighten.co.kr"
port = 8883
username = "smarthome.brighten.co.kr"
password = "smarthome1357!@"

sensor_topic = "tele/W220_818FB4/SENSOR"
state_topic = "tele/W220_818FB4/STATE"

# 클라이언트 생성
mqtt_client = mqtt.Client(f"publisher_test")

# ssl인증서 및 사용자, 암호 설정
mqtt_client.tls_set("/home/smarthome/cert/ca.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
mqtt_client.tls_insecure_set(True)
mqtt_client.username_pw_set(username, password)

# 브로커 연결 및 메세지 publish
mqtt_client.on_publish = on_publish
con_res = mqtt_client.connect(broker_address, port)
print(con_res)
mqtt_client.publish("test/topic", "hello broker")



# 처음 subscriber 실행한 후
# 버튼을 한번 눌렀을 때 - 2가지가 동시에 날아옴
# {'ZbReceived': {'0x7022': {'Device': '0x7022', '0008!00': 'FF0100', 'Dimmer': 255, 'Endpoint': 1, 'LinkQuality': 178}}}
# {'ZbReceived': {'0x7022': {'Device': '0x7022', '0300!0A': 'D2010100', 'CT': 466, 'Endpoint': 1, 'LinkQuality': 178}}}
'''
# Zigbee Smart Button
{
    # zigbee 통신으로 받은 메세지임을 뜻함
    'ZbReceived': {
        # 센서 및 장치의 id(번호)같은 것인 듯 => 게이트웨이 장치 정보에도 똑같이 나타남
        '0x7022': {
            # 디바이스 정보(이름 또는 id)
            'Device': '0x7022',
            # 특정 행동을 뜻하는 신호인듯(이거는 버튼 제조사의 공식문서 등을 찾아봐야할 듯), 행동에 대한 어떤 값이 나타남
            '0008!00': 'FF0100',
            # dimmer : 조광기, 조명의 밝기를 조절할 때 쓰는 장치 / 또는 주차
            # 빛의 밝기 정도를 나타내는 것이 아닐까, 누를 때마다 숫자가 바뀐다.
            'Dimmer': 255,
            'Endpoint': 1,
            'LinkQuality': 178
        }
    }
}
{
    'ZbReceived': {
        # 마찬가지로 스마트 버튼에서 날아온 정보
        '0x7022': {
            'Device': '0x7022', 
            # 특정 행동에 대한 어떤 값이 들어옴
            '0300!0A': 'D2010100', 
            # 얘는 뭐지, CT?
            'CT': 466,
            'Endpoint': 1, 
            'LinkQuality': 178
        }
    }
}
'''
# 꾹 눌렀을 때 : 3초 이상 꾹 누르고 있으면, 아래 신호가 1초마다 온다.(누른 상태 유지하면 계속 옴) 
# {'ZbReceived': {'0x7022': {'Device': '0x7022', '0008!02': '00550A00', 'DimmerStepUp': 85, 'Endpoint': 1, 'LinkQuality': 170}}}
# {'ZbReceived': {'0x7022': {'Device': '0x7022', '0008!02': '00550A00', 'DimmerStepUp': 85, 'Endpoint': 1, 'LinkQuality': 175}}}
# 버튼을 떼면 아래 신호가 온다.
# {'ZbReceived': {'0x7022': {'Device': '0x7022', '0008!03': '', 'DimmerStop': True, 'Endpoint': 1, 'LinkQuality': 165}}}
'''
{
    'ZbReceived': {
        '0x7022': {
            'Device': '0x7022', 
            # 버튼을 꾹 눌렀을 때 오는 신호 0008!02, 신호에 대한 값으로 000550A00이 찍힘
            '0008!02': '00550A00', 
            'DimmerStepUp': 85, 
            'Endpoint': 1, 
            'LinkQuality': 170
        }
    }
}
{
    'ZbReceived': {
        '0x7022': {
            'Device': '0x7022', 
            # 꾹 누르던 버튼을 떼면 오는 신호 0008!03, 값은 비어있음
            '0008!03': '', 
            'DimmerStop': True, 
            'Endpoint': 1, 
            'LinkQuality': 165
        }
    }
}
'''

# 왜인지는 모르겠으나, 두번 연속 누른 후에는 버튼에 대한 신호가 조금 바뀐다.
# 두번 연속 눌렀을 때 : 
# {'ZbReceived': {'0x7022': {'Device': '0x7022', '0006!00': '', 'Power': 0, 'Endpoint': 1, 'LinkQuality': 193}}}
'''
{
    'ZbReceived': {
        '0x7022': {
            'Device': '0x7022', 
            # 두번 연속 누름의 신호는 0006!00, 값은 비어있음
            '0006!00': '', 
            # 대신 Power라는 신호의 값이 0으로 들어옴
            'Power': 0, 
            'Endpoint': 1, 
            'LinkQuality': 193
        }
    }
}
'''
# 두번 연속 누른 후, 한번만 눌렀을 때
# {'ZbReceived': {'0x7022': {'Device': '0x7022', '0006!01': '', 'Power': 1, 'Endpoint': 1, 'LinkQuality': 188}}}
'''
{
    'ZbReceived': {
        '0x7022': {
            'Device': '0x7022', 
            # 한번만 눌렀을 때의 신호 0006!01, 값은 마찬가지로 비어있음
            '0006!01': '', 
            # Power 신호의 값은 1로 들어옴
            'Power': 1, 
            'Endpoint': 1, 
            'LinkQuality': 188
        }
    }
}
'''
# 이 두 경우가 나오는 조건은? 두번 누른 뒤, 한번 누르고, 조금 뒤에 한번만 눌렀을 때 날아옴
# {'ZbReceived': {'0x7022': {'Device': '0x7022', '0008!00': '3F0100', 'Dimmer': 63, 'Endpoint': 1, 'LinkQuality': 147}}}
# {'ZbReceived': {'0x7022': {'Device': '0x7022', '0300!06': 'A93F0100', 'HueSat': [169, 63], 'Endpoint': 1, 'LinkQuality': 160}}}
'''
{
    'ZbReceived': {
        '0x7022': {
            'Device': '0x7022',
            '0008!00': '3F0100', 
            'Dimmer': 63, 
            'Endpoint': 1, 
            'LinkQuality': 147
        }
    }
}

{
    'ZbReceived': {
        '0x7022': {
            'Device': '0x7022', 
            '0300!06': 'A93F0100', 
            # Hue : 색상, Sat(Saturation) : 채도
            'HueSat': [169, 63], 
            'Endpoint': 1, 
            'LinkQuality': 160
        }
    }
}
'''


# 아래는 새로 들어온 다른 메세지
# {'Time': '2023-07-28T13:40:57', 'SHTCX': {'Temperature': 27.9, 'Humidity': 20.7, 'DewPoint': 3.3}, 'TempUnit': 'C'}
# {'Time': '2023-07-28T13:45:57', 'SHTCX': {'Temperature': 27.9, 'Humidity': 20.9, 'DewPoint': 3.4}, 'TempUnit': 'C'}
# {'Time': '2023-07-28T13:50:57', 'SHTCX': {'Temperature': 28.0, 'Humidity': 20.6, 'DewPoint': 3.3}, 'TempUnit': 'C'}
'''
# 게이트웨이가 시간에 따라 자동적으로 던지는 시간, 온도, 습도 정보인 것 같다. 5분 간격으로 메세지를 보낸다.
{
    # 시간이 나타나있다.
    'Time': '2023-07-28T13:40:57',
    # 온도와 습도, 이슬점(응결점)이 나타나있다.
    'SHTCX': {
        # 
        'Temperature': 27.9, 
        'Humidity': 20.7, 
        'DewPoint': 3.3
    }, 
    # 온도 단위는 섭씨
    'TempUnit': 'C'
}
'''


# 충격 감지 센서

'''
{
    'ZbReceived': {
        '0xE30E': {
            'Device': '0xE30E', 
            '0500?00': '010400010000', 
            'ZoneStatusChange': 1025, 
            'ZoneStatusChangeZone': 1, 
            'Movement': 1, 
            'Endpoint': 1, 
            'LinkQuality': 141
        }
    }
}
'''


# 사람 감지 센서
'''
{
    'ZbReceived': {
        '0xB6A8': {
            'Device': '0xB6A8', 
            'EF00/026D': 119, 
            'Endpoint': 1, 
            'LinkQuality': 180
        }
    }
}

{
    'ZbReceived': {
        '0xB6A8': {
            'Device': '0xB6A8', 
            'EF00/0268': 388, 
            'Endpoint': 1, 
            'LinkQuality': 183
        }
    }
}
'''
