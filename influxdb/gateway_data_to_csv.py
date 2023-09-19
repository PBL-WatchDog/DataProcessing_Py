import influxdb_client
import json

from dotenv import load_dotenv
import os
load_dotenv()

# Initialize InfluxDB client
token = "blQNLEOIYKlbJ73tWhurIedUOGQSxtfR0eHPGjPlF0LPWxi92dFuCcWwv1K0JoXjHdHiRCqiSHZfihv-PPJfWw=="
org = "Brighten"
url = "http://localhost:8086"
bucket = "Sensor_test"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

query = f"""
            import "json"

            from(bucket: "Sensor_test")
                |> range(start: -1y)
                |> filter(fn: (r) => r._measurement == \"GatewayData\")
                |> filter(fn: (r) => r._field == \"humidity\")
                |> window(every: 30m)
                |> mean()
                |> map(fn: (r) => ({"{"}r with jsonStr: string(v: json.encode(v: {"{"}"measurement": r._measurement, "r._field": r._field, "mac_address": r.mac_address, "date": r._start, "value": r._value{"}"})){"}"}))
            """
# |> filter(fn: (r) => r[\"mac_address\"] == \"W220_D6FC80\")
# Execute the query and fetch the result

result = query_api.query(query, org=org)
# json으로 파싱 -> > 출력 재지정자로 바로 .json 파일로 저장
print("{")
i = 0
for table in result:
    for record in table.records:
        print('"' + str(i) + '"' + ": ")
        data = json.loads(record.__getitem__('jsonStr'))
        print(data, end='')
        print(",")
        i += 1
print("}")

# # Convert the result to a DataFrame
# df = pd.DataFrame(result['Sensor_test'])

# # Save the DataFrame to a CSV file
# df.to_csv('./sensor.csv', index=False)
