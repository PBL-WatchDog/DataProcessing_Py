# 패키지 로딩
library(prophet)

# 데이터 로딩 (예시)
df <- read.csv("C:/Users/김두현/Desktop/경북 공모전/data/gateway/818_no.csv")
df$date <- as.POSIXct(df$date, format="%Y-%m-%d %H:%M:%S")

# 날짜와 변수 컬럼만 선택해서 Prophet 모델에 적용할 데이터프레임 생성
prophet_df_temp <- data.frame(ds = df$date, y = df$temperature)
prophet_df_humidity <- data.frame(ds = df$date, y = df$humidity)
prophet_df_dew_point <- data.frame(ds = df$date, y = df$dew_point)

# 모델 생성 및 학습 (온도)
model_temp <- prophet(prophet_df_temp)
forecast_temp <- predict(model_temp, prophet_df_temp)

# 모델 생성 및 학습 (습도)
model_humidity <- prophet(prophet_df_humidity)
forecast_humidity <- predict(model_humidity, prophet_df_humidity)

# 모델 생성 및 학습 (이슬점)
model_dew_point <- prophet(prophet_df_dew_point)
forecast_dew_point <- predict(model_dew_point, prophet_df_dew_point)

# 보간된 값을 원래 데이터프레임에 저장
df$temperature <- forecast_temp$yhat
df$humidity <- forecast_humidity$yhat
df$dew_point <- forecast_dew_point$yhat


View(df)
draw_line_graph(df)


df$date <- format(df$date, "%Y-%m-%d %H:%M:%S")
write.csv(df, "C:/Users/김두현/Desktop/경북 공모전/data/gateway/818_final.csv", row.names = FALSE)

#################################################################################

# 데이터 로딩 (예시)
df <- read.csv("C:/Users/김두현/Desktop/경북 공모전/data/gateway/d6f_no.csv")
df$date <- as.POSIXct(df$date, format="%Y-%m-%d %H:%M:%S")

# 날짜와 변수 컬럼만 선택해서 Prophet 모델에 적용할 데이터프레임 생성
prophet_df_temp <- data.frame(ds = df$date, y = df$temperature)
prophet_df_humidity <- data.frame(ds = df$date, y = df$humidity)
prophet_df_dew_point <- data.frame(ds = df$date, y = df$dew_point)

# 모델 생성 및 학습 (온도)
model_temp <- prophet(prophet_df_temp)
forecast_temp <- predict(model_temp, prophet_df_temp)

# 모델 생성 및 학습 (습도)
model_humidity <- prophet(prophet_df_humidity)
forecast_humidity <- predict(model_humidity, prophet_df_humidity)

# 모델 생성 및 학습 (이슬점)
model_dew_point <- prophet(prophet_df_dew_point)
forecast_dew_point <- predict(model_dew_point, prophet_df_dew_point)

# 보간된 값을 원래 데이터프레임에 저장
df$temperature <- forecast_temp$yhat
df$humidity <- forecast_humidity$yhat
df$dew_point <- forecast_dew_point$yhat


View(df)
draw_line_graph(df)


df$date <- format(df$date, "%Y-%m-%d %H:%M:%S")
write.csv(df, "C:/Users/김두현/Desktop/경북 공모전/data/gateway/d6f_final.csv", row.names = FALSE)
