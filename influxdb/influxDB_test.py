from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
# import influxdb_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB 정보
bucket = "Sensor_test"     # bucket은 database와 동일
org = "Brighten"
token = "QKxY9cgaqOJL8SZ8oDqqg_UsiRq3Dr9MaHIFJPuJ-C_9xrGKjpycifTAXKFbT3gaDpq2MbxCdt9Sus8Oz6pnQg=="
url = "http://210.123.135.176:8086"

# 클라이언트 설정
client = InfluxDBClient(
        url = url,
        token = token,
        org = org
)

# 클라이언트에서 사용할 API 생성(write, query)
write_api = client.write_api(write_options = SYNCHRONOUS)
query_api = client.query_api()

'''
point(record) 만드는 예시
'''
# Point 클래스 이용
# measurement는 table과 동일
point1 = Point("[measurement 이름]").tag("[tag(PK Column 또는 Indexed Column(주키 속성)) 이름]", "[tag 의 값]")\
            .field("[field(Unindexed Column(일반적인 속성)) 이름]", "field의 값")

'''
Query 사용 예시
'''
# Table structure 이용
# end_date_obj = datetime.strptime(datetime().now(), "%y-%m-%d")   # 문자열 형태의 날짜를 datetime 객체로 변환
# start_date_obj = end_date_obj - timedelta(days=7)         # 시작 날짜로부터 7일 전의 날짜 계산
query = f"""

import "json"

from(bucket: "Sensor_test")
    |> range(start: 2023-08-01T00:00:00Z, stop: 2023-08-06T00:00:00Z)
    |> filter(fn: (r) => r._measurement == "GatewayData" and r._field == "temperature" and r.mac_address == "W220_818FB4")
    |> window(every: 1d)
    |> mean()
    |> map(fn: (r) => ({"{"}r with jsonStr: string(v: json.encode(v: {"{"}"date": r._start, "value": r._value{"}"})){"}"}))

    """
tables = query_api.query(query)

for table in tables:
    print(table)
    for record in table.records:
        print(record.values)
        print(record.__getitem__('jsonStr'))
        print()


# Bind parameters 이용
# 검색 조건을 딕셔너리 형태로 설정하여 쿼리 api의 parameter로 보낸다. 
# p = {"_start": datetime.timedelta(hours=-1),
#      "_location": "Prague",
#      "_desc": True,
#      "_floatParam": 25.1,
#      "_every": datetime.timedelta(minutes=5)
#      }

# <measurement>[,<tag-key>=<tag-value>...] <field-key>=<field-value>[,<field2-key>=<field2-value>...] [unix-nano-timestamp]
# tables = query_api.query('''
#     from(bucket:"my-bucket") |> range(start: _start)
#         |> filter(fn: (r) => r["_measurement"] == "my_measurement")
#         |> filter(fn: (r) => r["_field"] == "temperature")
#         |> filter(fn: (r) => r["location"] == _location and r["_value"] > _floatParam)
#         |> aggregateWindow(every: _every, fn: mean, createEmpty: true)
#         |> sort(columns: ["_time"], desc: _desc)
# ''', params=p)

# for table in tables:
#     print(table)
#     for record in table.records:
#         print(str(record["_time"]) + " - " + record["location"] + ": " + str(record["_value"]))

# def make_point(tablename, timestamp, dic):
#   point = {
#       'tags': dic['tags'],
#       'fields': dic['fields'],
#       'time': timestamp
#   }
#   return point

# temp = Blueprint('temp', __name__)

# @temp.route('/week', methods=['GET'])
# @jwt_required()
# def get_temperature_by_week():
#     user_id = get_jwt_identity()
#     target_date = request.args.get('date')
    
#     db = pymysql.connect(host='211.57.200.6', port=3306, user='root', password='willcam1190', db='smarthome', charset='utf8')
#     cursor = db.cursor(pymysql.cursors.DictCursor)
#     # 일주일 각 일의 온도 평균을 select
#     sql = f"""
#     SELECT DATE_FORMAT(date, '%m-%d') as day, avg(temp) as temp
#     FROM Temp_humi 
#     WHERE date BETWEEN DATE_ADD(DATE('{target_date}'), INTERVAL -1 week) AND DATE('{target_date}')+1
#     AND user_id = {user_id}
#     GROUP BY date(date);
#     """

#     cursor.execute(sql)
#     result = cursor.fetchall()
#     print(result)
#     db.close()
#     return jsonify(result)

# @temp.route('/day', methods=['GET'])
# @jwt_required()
# def get_temperature_by_day():
#     user_id = get_jwt_identity()
#     target_date = request.args.get('date')
    
#     db = pymysql.connect(host='211.57.200.6', port=3306, user='root', password='willcam1190', db='smarthome', charset='utf8')
#     cursor = db.cursor(pymysql.cursors.DictCursor)
#     sql = f"""
#     SELECT DATE_FORMAT(date, '%H') as hour, temp
#     FROM Temp_humi 
#     WHERE DATE(date) = '{target_date}' AND user_id = {user_id} 
#     GROUP BY HOUR(date);
#     """

#     cursor.execute(sql)
#     result = cursor.fetchall()
#     print(result)
#     db.close()
#     return jsonify(result)
