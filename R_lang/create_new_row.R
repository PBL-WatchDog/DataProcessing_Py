library(ggplot2)
library(lubridate)
library(dplyr)

df <- read.csv("C:/Users/김두현/Desktop/경북 공모전/data/gateway/gateway.csv")
df$date <- as.POSIXct(df$date, format="%Y-%m-%d %H:%M:%S")


draw_line_graph <- function(df){
  title <- paste(df$gateway[0], "Temperature, Humidity, and Dew Point over Time")
  
  ggplot(df, aes(x=date)) +
    geom_line(aes(y=temperature, color="Temperature")) +
    geom_line(aes(y=humidity, color="Humidity")) +
    geom_line(aes(y=dew_point, color="Dew Point")) +
    labs(title = title,
         x = "Date",
         y = "Value",
         color = "Legend")
}



# 달이 넘어가는 부분에 대한 보간 -> create_new_row 함수로는 감지 못 함
interpolate_row <- function(df){
  # 날짜 범위 설정
  start_date <- min(df$date, na.rm = TRUE)
  end_date <- max(df$date, na.rm = TRUE)
  
  # 30분 단위로 날짜 생성
  all_dates <- seq(from = start_date, to = end_date, by = "30 min")
  
  # 모든 날짜를 포함하도록 데이터프레임 확장
  new_df <- data.frame(
    date = all_dates,
    temperature = NA,
    humidity = NA,
    dew_point = NA,
    stringsAsFactors = FALSE
  )
  new_df$date <- as.POSIXct(new_df$date, origin='1970-01-01') # date type 변환
  
  # 원래 데이터와 병합
  df <- merge(new_df, df, by = "date", all.x = TRUE)

  # coalesce를 사용해 컬럼 통합
  df <- df %>%
    mutate(
      temperature = coalesce(temperature.x, temperature.y),
      humidity = coalesce(humidity.x, humidity.y),
      dew_point = coalesce(dew_point.x, dew_point.y)
    ) %>%
    select(-contains(".x"), -contains(".y")) # 불필요한 컬럼 제거
  
  return (df)
}


# 게이트웨이 별로 데이터 프레임 분리
df_818 <- df[df$gateway == 'W220_818FB4', ]
df_d6f <- df[df$gateway == 'W220_D6FC80', ]


df_818 <- interpolate_row(df_818)
df_d6f <- interpolate_row(df_d6f)
df_818$gateway <- "W220_818FB4"
df_d6f$gateway <- "W220_D6FC80"


draw_line_graph(df_818)
draw_line_graph(df_d6f)

df_818$date <- format(df_818$date, "%Y-%m-%d %H:%M:%S")
df_d6f$date <- format(df_d6f$date, "%Y-%m-%d %H:%M:%S")
write.csv(df_818, "C:/Users/김두현/Desktop/경북 공모전/data/gateway/818_no.csv", row.names = FALSE)
write.csv(df_d6f, "C:/Users/김두현/Desktop/경북 공모전/data/gateway/d6f_no.csv", row.names = FALSE)


