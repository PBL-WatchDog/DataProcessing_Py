library(jsonlite)

json_temp <- fromJSON("C:/Users/김두현/Desktop/경북 공모전/data/gateway/temperature.json")
json_humi <- fromJSON("C:/Users/김두현/Desktop/경북 공모전/data/gateway/humidity.json")
json_dew <- fromJSON("C:/Users/김두현/Desktop/경북 공모전/data/gateway/dew_point.json")

n <- length(json_temp) # json_temp의 길이로 n을 초기화. 필요에 따라 수정 가능

# 빈 데이터프레임 생성
df <- data.frame(
  gateway = character(n),
  date = as.POSIXct(rep(NA, n), origin='1970-01-01'),
  temperature = numeric(n),
  humidity = numeric(n),
  dew_point = numeric(n),
  stringsAsFactors = FALSE
)

# 데이터프레임에 값 채우기
for(i in 1:n){
  df$gateway[i] <- json_temp[[i]]$mac_address
  df$date[i] <- as.POSIXct(json_temp[[i]]$date, format="%Y-%m-%dT%H:%M:%OSZ", tz="UTC")
  df$temperature[i] <- json_temp[[i]]$value
  df$humidity[i] <- json_humi[[i]]$value
  df$dew_point[i] <- json_dew[[i]]$value
}

# 데이터프레임 확인
df$date <- format(df$date, "%Y-%m-%d %H:%M:%S")
write.csv(df, "C:/Users/김두현/Desktop/경북 공모전/data/gateway/gateway.csv", row.names = FALSE)

