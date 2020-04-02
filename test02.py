#!/usr/bin/env python3 
#pandas 기초 익히기 (서울시 범죄 현황 분석)
import pandas as pd
import numpy as np

df = pd.read_excel('02. sales-funnel.xlsx')
print(df.head())

#Name항목으로만 정렬(pivot_table 사용), 중복된 Name의 항목은 하나로 합쳐지고 value들은 평균을 갖는다.
print(pd.pivot_table(df, index=["Name"]))

#Index를 여러개 지정
print(pd.pivot_table(df, index=["Name","Rep","Manager"]))

#특정 value만 지정 (value를 pivot_table로 합친 경우 평균치가 기본이 된다.)
print(pd.pivot_table(df, index=["Name","Rep"], values=["Price"]))

#합계를 사용하려면 aggfunc 옵션을 사용해서 np.sum을 사용
print(pd.pivot_table(df, index=["Name","Rep"], values=["Price"], aggfunc=np.sum))

#np.sum(합계), np.mean(평균), fill_value옵션으로 Nan처리
print(pd.pivot_table(df, index=["Name","Rep","Product"], values=["Price","Quantity"], aggfunc=[np.sum,np.mean], fill_value=0, margins=True))

#시각화 도구 Seaborn
import matplotlib.pyplot as plt
import seaborn as sns

x = np.linspace(0, 14, 100)
y1 = np.sin(x)
y2 = 2*np.sin(x+0.5)
y3 = 3*np.sin(x+1.0)
y4 = 4*np.sin(x+1.5)

plt.figure(figsize=(10,6))
plt.plot(x,y1, x,y2, x,y3, x,y4)
plt.show()

sns.set_style("whitegrid")  #seaborn에서 지원하는 whitegrid 스타일
plt.figure(figsize=(10,6))
plt.plot(x,y1, x,y2, x,y3, x,y4)
plt.show()

#Tips데이터셋 (요일별 점심,저녁,흡연여부,식사금액,팁을 정리한 데이터)
tips = sns.load_dataset("tips")
print(tips.head(5))

#x축은 요일, y축은 전체 금액
plt.figure(figsize=(8,6))
sns.boxenplot(x="day", y="total_bill", data=tips)
plt.show()

#hue옵션을 이용하여 흡연여부 구분, palette로 색상지정
plt.figure(figsize=(8,6))
sns.boxenplot(x="day", y="total_bill", hue="smoker", data=tips, palette="Set3")
plt.show()

#darkgrid스타일에 lmplot로 그리기
sns.set_style("darkgrid")
sns.lmplot(x="total_bill", y="tip", hue="smoker", data=tips, palette="Set1", size=7)
plt.show()

#연도 및 월별 항공기 승객수 데이터셋
flights = sns.load_dataset("flights")
print(flights.head(5))

#pivot을 이용하여 월별, 연도별로 구분
flights = flights.pivot("month", "year", "passengers")
print(flights.head(5))

#heatmap으로 그리기 (경향을 설명하기 좋음)
plt.figure(figsize=(10,8))
sns.heatmap(flights, annot=True, fmt="d")
plt.show()

#아이리스 꽃에 대한 데이터셋(꽃잎, 꽃받침의 너비와 폭, 종류)
sns.set(style="ticks")
iris = sns.load_dataset("iris")
print(iris.head(5))

#pairplot로 그리기 (종류별로 나눌때)
sns.pairplot(iris, hue="species")
plt.show()

#지도 시각화 도구 Folium (터미널창에서 pip install folium)
import folium
#위도 경도 입력, zoom_start옵션 확대비율 정의, 
map_osm = folium.Map(location=[45.5236, -122.6750], zoom_start=13)
#크롬으로 맵 확인
map_osm.save('map1.html')
#tiles옵션으로 다양한 모양의 지도
map_osm = folium.Map(location=[45.5236, -122.6750], tiles='Stamen Toner', zoom_start=13)
map_osm.save('map2.html')

map_2 = folium.Map(location=[45.5236, -122.6750], tiles='Stamen Toner', zoom_start=13)
#지도에 마크 표시
folium.Marker([45.5244, -122.6699], popup='The Waterfront').add_to(map_2)
#지도에 원 표시, raduis옵션 반경, color옵션 색상
folium.CircleMarker([45.5215, -122.6261], radius=50, popup='Laurelhurst Park', color='#3186cc', fill_color='#3186cc', ).add_to(map_2)
map_2.save('map3.html')

#2012년 10월 기준 미국의 주별 실업률
state_data = pd.read_csv('02. folium_US_Unemployment_Oct2012.csv')
print(state_data.head())
#json파일
state_geo = '02. folium_us-states.json'
map = folium.Map(location=[40, -98], zoom_start=4)
#json파일과 지도에 표현하고 싶은 데이터를 입력하여 지도에 시각화.
#key_on옵션 지도의 id입력, legend_name옵션 지도상단 바 이름
map.choropleth(geo_data=state_geo, data=state_data, columns=['State', 'Unemployment'], 
               key_on='feature.id', fill_color='YlGn', legend_name='Unemployment Rate (%)')
map.save('map4.html')
