library(jsonlite)
library(ggplot2)

sensor1 <- fromJSON("C:/Users/김두현/Desktop/경북 공모전/data/sensor/D6FC80_sensor.json")

sensor1_n <- length(sensor1) / 2
cat(sensor1_n)

df1 <- data.frame(
  gateway = character(sensor1_n),
  date = as.POSIXct(rep(sensor1_n), origin='1970-01-01'),
  door_sensor = numeric(sensor1_n),
  motion_sensor = numeric(sensor1_n),
  stringsAsFactors = FALSE
)


# 데이터프레임에 값 채우기
for(i in 1:sensor1_n){
  df1$gateway[i] <- sensor1[[i]]$mac_address
  df1$date[i] <- as.POSIXct(sensor1[[i]]$date, format="%Y-%m-%dT%H:%M:%OSZ", tz="UTC")
  df1$door_sensor[i] <- sensor1[[i]]$count
  df1$motion_sensor[i] <- sensor1[[(sensor1_n + i)]]$count
}


# 데이터프레임 확인
View(df1)

# 이어진 줄 그래프 그리기
ggplot(df1, aes(x=date)) +
  geom_line(aes(y=door_sensor, color='Door Sensor')) +
  geom_line(aes(y=motion_sensor, color='Motion Sensor')) +
  labs(title="Sensor Data Over Time",
       x= "Time",
       y= "Sensor Value")
  + theme_minimal()

write.csv(df1, "C:/Users/김두현/Desktop/경북 공모전/data/sensor/D6FC80_sensor.csv", row.names = FALSE)

#########################################################################################

sensor2 <- fromJSON("C:/Users/김두현/Desktop/경북 공모전/data/sensor/818FB4_sensor.json")

sensor2_n <- length(sensor2) / 4
cat(sensor2_n)

df2 <- data.frame(
  gateway = character(sensor2_n),
  date = as.POSIXct(rep(sensor2_n), origin='1970-01-01'),
  door_sensor = numeric(sensor2_n),
  motion_sensor = numeric(sensor2_n),
  stringsAsFactors = FALSE
)


# 데이터프레임에 값 채우기
for(i in 1:sensor2_n){
  df2$gateway[i] <- sensor2[[i]]$mac_address
  df2$date[i] <- as.POSIXct(sensor2[[i]]$date, format="%Y-%m-%dT%H:%M:%OSZ", tz="UTC")
  
  df2$motion_sensor[i] <- sensor2[[i]]$count
  df2$door_sensor[i] <- sensor2[[(sensor2_n*2 + i)]]$count
  df2$door_sensor[i] <- df2$door_sensor[i] + sensor2[[(sensor2_n + i)]]$count
  df2$door_sensor[i] <- df2$door_sensor[i]+ sensor2[[(sensor2_n*3 + i)]]$count
}


# 데이터프레임 확인
View(df2)

# # 이어진 줄 그래프 그리기
# ggplot(df2, aes(x=date)) +
#   geom_line(aes(y=door_sensor, color='Door Sensor')) +
#   geom_line(aes(y=motion_sensor, color='Motion Sensor')) +
#   labs(title="Sensor Data Over Time",
#        x= "Time",
#        y= "Sensor Value")
# + theme_minimal()

write.csv(df2, "C:/Users/김두현/Desktop/경북 공모전/data/sensor/818FB4_sensor.csv", row.names = FALSE)
