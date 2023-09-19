import influxdb_client
import json

from dotenv import load_dotenv
import os
load_dotenv()

# Initialize InfluxDB client
token = os.environ.get("INFLUX_API_KEY")
org = "Brighten"
url = "http://localhost:8086"
bucket = "Sensor_test"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()
# Define the query
query = f"""
        import "json"
        import "experimental"

            from(bucket: "Sensor_test")
                |> range(start: 2023-08-22T00:00:00Z)
                |> filter(fn: (r) => r._measurement == \"SensorData\")
                |> filter(fn: (r) => r[\"mac_address\"] == \"W220_818FB4\")
                |> filter(fn: (r) => r[\"Device\"] == \"0x5D36\" or r[\"Device\"] == \"0x7022\" or r[\"Device\"] == \"0x8015\" or r[\"Device\"] == \"0xE30E\")
                |> aggregateWindow(every: 30m, fn: count, createEmpty: true)
                |> fill(column: "_value", value: 0)
                |> map(fn: (r) => ({"{"}r with jsonStr: string(v: json.encode(v: {"{"}"measurement": r._measurement, "r.Device": r.Device, "mac_address": r.mac_address, "date": r._time, "count": r._value{"}"})){"}"}))
        """
# or r[\"Device\"] == \"0x5D36\" or r[\"Device\"] == \"0x7022\" or r[\"Device\"] == \"0x8015\" or r[\"Device\"] == \"0xE30E\"
# r[\"Device\"] == \"0xF26E\" or r[\"Device\"] == \"0xC5FF\"
# Execute the query and fetch the result
result = query_api.query(query, org=org)

# json으로 파싱 -> > 출력 재지정자로 바로 .json 파일로 저장
print("{")
i = 0
for table in result:
    for record in table.records:
        print('"' + str(i) + '"' + ": ")
        data = json.loads(record.__getitem__("jsonStr"))
        print(json.dumps(data), end='')
        print(",")
        i += 1
print("}")
