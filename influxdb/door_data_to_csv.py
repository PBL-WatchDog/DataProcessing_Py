import influxdb_client
import pandas as pd

token = "1cDBU-BVSjJ0emb2KmZjgOhGNs3V1-cW60aqfMHoaeyndLVVdFfIo_Gp81OZn1iZ6gCHUvTjoi2rheflojizOg=="
org = "Brighten"
url = "http://211.57.200.6:8086"
bucket = "smarthome"


client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()


# dataframe 생성
device_type = "door"
# df = pd.DataFrame(columns=["date", "mac_address", f"{device_type}1", f"{device_type}2", f"{device_type}3"])

query = f"""
            from(bucket: "{bucket}")
                |> range(start: 2023-08-18)
                |> filter(fn: (r) => r["_measurement"] == "SensorData")
                |> filter(fn: (r) => r["mac_address"] == "W220_D6FC80")
                |> filter(fn: (r) => r["Device"] == "0x5722" or r["Device"] == "0x838A" or r["Device"] == "0xC5FF")
                |> filter(fn: (r) => r["_field"] == "0500?00")
                |> aggregateWindow(every: 30m, fn: count, createEmpty: true)
                |> fill(column: "_value", value: 0)
         """

result = query_api.query(query, org=org)

data = []
data_dict = {}

device_col = {
    "0x5722": device_type + "1",
    "0x838A": device_type + "2",
    "0xC5FF": device_type + "3"
}

for table in result:
    for record in table.records:
        date = record["_time"]
        mac_address = record["mac_address"]
        device = record["Device"]
        value = record["_value"]
        if not (date.strftime("%Y-%m-%d %H:%M:%S") + "~" + mac_address) in data_dict:
            data_dict[date.strftime("%Y-%m-%d %H:%M:%S") + "~" + mac_address] = {}
        
        data_dict[date.strftime("%Y-%m-%d %H:%M:%S") + "~" + mac_address][device_col[device]] = value
        # data.append({"date": date, "mac_address": mac_address, field: value})
# 데이터프레임 생성
for key, value in data_dict.items():
    date = key.split("~")[0]
    mac_address = key.split("~")[1]

    obj = {}
    obj['date'] = date;
    obj['mac_address'] = mac_address

    for device_id, col_name in device_col.items():
        obj[col_name] = value.get(col_name, 0) 

    data.append(obj)

df = pd.DataFrame(data)

df.to_csv(f"./data/{device_type}/{mac_address}_{device_type}.csv", index=False)