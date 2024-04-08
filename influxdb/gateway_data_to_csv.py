import influxdb_client
import pandas as pd

token = "1cDBU-BVSjJ0emb2KmZjgOhGNs3V1-cW60aqfMHoaeyndLVVdFfIo_Gp81OZn1iZ6gCHUvTjoi2rheflojizOg=="
org = "Brighten"
url = "http://211.57.200.6:8086"
bucket = "smarthome"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

for mac_address in ["W220_8929E8", "W220_D6FC80", "W220_818FB4", "W220_BADBD8"]:
    # dataframe 생성
    df = pd.DataFrame(columns=["date", "mac_address", "temperature", "humidity", "dew_point"])

    query = f"""
                from(bucket: "{bucket}")
                    |> range(start: 0)
                    |> filter(fn: (r) => r._measurement == \"GatewayData\")
                    |> filter(fn: (r) => r._field == \"temperature\" or r._field == \"humidity\" or r._field == \"dew_point\")
                    |> filter(fn: (r) => r[\"mac_address\"] == "{mac_address}")
                    |> window(every: 30m)
                    |> mean()
            """

    result = query_api.query(query, org=org)

    data = []
    data_dict = {}

    for table in result:
        for record in table.records:
            date = record["_start"]
            mac_address = record["mac_address"]
            field = record["_field"]
            value = record["_value"]
            if not (date.strftime("%Y-%m-%d %H:%M:%S") + "~" + mac_address) in data_dict:
                data_dict[date.strftime("%Y-%m-%d %H:%M:%S") + "~" + mac_address] = {}
            
            data_dict[date.strftime("%Y-%m-%d %H:%M:%S") + "~" + mac_address][field] = value
            # data.append({"date": date, "mac_address": mac_address, field: value})

    # 데이터프레임 생성
    for key, value in data_dict.items():
        date = key.split("~")[0]
        mac_address = key.split("~")[1]
        data.append({"date": date, "mac_address": mac_address, "temperature": value["temperature"], "humidity": value["humidity"], "dew_point": value["dew_point"]})
    
    df = pd.DataFrame(data)
   
    df.to_csv(f"./data/gateway/{mac_address}.csv", index=False)