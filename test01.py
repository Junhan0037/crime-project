#!/usr/bin/env python3 
#서울시 범죄 현황 분석
import pandas as pd
import numpy as np

crime_anal_police = pd.read_csv('02. crime_in_Seoul.csv', thousands=',', encoding='euc-kr')
print(crime_anal_police)

#강남3구를 알고싶은데 관서별로 되어 있으니 구정보를 알기위해 Google Maps API 이용
'''
1. https://console.developers.google.com/apis/dashboard에서 Google Maps Geocoding API접근하여 API키 받기
2. 터미널창에서 pip install googlemaps 설치
'''
#Google Maps API 로그인
import googlemaps
gmaps_key = "AIzaSyDMgtEhS_gxWY2RETnV-wdUFa3UoH2xOPM"
gmaps = googlemaps.Client(key=gmaps_key)

#formatted_address항목 주소, lng항목 위도, lat항목 경도 정보확인!
print(gmaps.geocode('서울중부경찰서', language='ko'))

station_name = []
for name in crime_anal_police['관서명']:
    #name[:-1]을 이용하여 끝에 한글자를 제외
    station_name.append('서울'+str(name[:-1])+'경찰서')
print(station_name)

#주소, 위도, 경도 크롤링
station_address = []
station_lat = []
station_lng = []
for name in station_name:
    tmp = gmaps.geocode(name, language='ko')
    station_address.append(tmp[0].get("formatted_address"))
    tmp_loc = tmp[0].get("geometry")
    station_lat.append(tmp_loc['location']['lat'])
    station_lng.append(tmp_loc['location']['lng'])
    #print(name + '-->' + tmp[0].get("formatted_address"))
print(station_address)
print(station_lat)
print(station_lng)

#구이름을 추출하여 '구별'열에 추가
gu_name = []
for name in station_address:
    tmp = name.split()
    tmp_gu = [gu for gu in tmp if gu[-1] == '구'][0]
    gu_name.append(tmp_gu)
crime_anal_police['구별'] = gu_name
print(crime_anal_police.head())

#예외처리 (금천경찰서는 관악구에 위치하여 있어서 금천구로 변경해준다)
print(crime_anal_police[crime_anal_police['관서명']=='금천서'])
crime_anal_police.loc[crime_anal_police['관서명']=='금천서', ['구별']] = '금천구'
print(crime_anal_police[crime_anal_police['관서명']=='금천서'])

#encoding="cp949"를 이용하면 한글깨짐 해결
crime_anal_police.to_csv('02. crime_in_Seoul_include_gu_name.csv', sep=',', encoding='utf-8')

#index_col=0을 이용하여 index 없애기
crime_anal_raw = pd.read_csv('02. crime_in_Seoul_include_gu_name.csv', encoding='utf-8', index_col=0)
#관서별에서 구별로 정렬 (중복데이터 합치기, 관서명 항목 제거)
crime_anal = pd.pivot_table(crime_anal_raw, index='구별', aggfunc=np.sum)
print(crime_anal.head)

#필요한 열 및 필요없는 열 추가, 삭제
crime_anal['강간검거율'] = crime_anal['강간 검거'] / crime_anal['강간 발생'] * 100
crime_anal['강도검거율'] = crime_anal['강도 검거'] / crime_anal['강도 발생'] * 100
crime_anal['살인검거율'] = crime_anal['살인 검거'] / crime_anal['살인 발생'] * 100
crime_anal['절도검거율'] = crime_anal['절도 검거'] / crime_anal['절도 발생'] * 100
crime_anal['폭력검거율'] = crime_anal['폭력 검거'] / crime_anal['폭력 발생'] * 100
del crime_anal['강간 검거']
del crime_anal['강도 검거']
del crime_anal['살인 검거']
del crime_anal['절도 검거']
del crime_anal['폭력 검거']
print(crime_anal.head())

#검거율이 100%이상인 데이터는 100으로 통일
con_list = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']
for column in con_list:
    crime_anal.loc[crime_anal[column] > 100, column] = 100
print(crime_anal.head())

#열이름 수정 (서울시 구별 5대 번죄의 발생건수, 검거율 데이터 추출 성공!)
crime_anal.rename(columns = {'강간 발생':'강간',
                             '강도 발생':'강도',
                             '살인 발생':'살인',
                             '절도 발생':'절도',
                             '폭력 발생':'폭력'}, inplace=True)
print(crime_anal.head())

#각 컬럼별로 '정규화'
from sklearn import preprocessing
col = ['강간', '강도', '살인', '절도', '폭력']

x = crime_anal[col].values
min_max_scaler = preprocessing.MinMaxScaler()

x_scaled = min_max_scaler.fit_transform(x.astype(float))
crime_anal_norm = pd.DataFrame(x_scaled, columns = col, index = crime_anal.index)

col2 = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']
crime_anal_norm[col2] = crime_anal[col2] #검거율 데이터는 그대로 붙여넣기
print(crime_anal_norm.head())

#CCTV 파일을 읽어서 인구수와 CCTV계수 불러오기
result_CCTV = pd.read_csv('CCTV_result.csv', encoding='utf-8', index_col='구별')
crime_anal_norm[['인구수', 'CCTV']] = result_CCTV[['인구수', '소계']]
print(crime_anal_norm.head())

#합계를 이용해 '범죄', '검거'열 생성. aixs옵션 0은 x축, 1은 y축 합계
col = ['강간', '강도', '살인', '절도', '폭력']
crime_anal_norm['범죄'] = np.sum(crime_anal_norm[col], axis=1)
col = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']
crime_anal_norm['검거'] = np.sum(crime_anal_norm[col], axis=1)
print(crime_anal_norm.head())

#시각화 도구 Seaborn (터미널창에서 pip install seaborn)
import matplotlib.pyplot as plt
import seaborn as sns

#matplotlib 폰트 변경 (한글지원 X 때문)
import platform
from matplotlib import font_manager, rc
plt.rcParams['axes.unicode_minus'] = False
if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    path = "c:\Windows\Fonts\malgun.ttf"
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system... sorry~~~~')

#pairplot로 그려서 상관관계 그래프 출
sns.pairplot(crime_anal_norm, vars=["강도", "살인", "폭력"], kind='reg', size=3)
plt.show()  #결과 : 강도와 살인 모두 양의 상관관계를 보인다.

#인구수와 CCTV 개수, 살인과 강도의 상관관계 출력
sns.pairplot(crime_anal_norm, x_vars=["인구수", "CCTV"], y_vars=["살인", "강도"], kind='reg', size=3)
plt.show()  #결과 : CCTV와 살인 관계가 낮은지 몰라도 CCTV가 없을때 살인이 많이 일어나는 구간 존재
            #즉, CCTV 개수를 기준으로 좌측면에 살인,강도의 높은 수를 갖는 데이터 확인

#인구수와 CCTV 개수, 살인검거율과 강도검거율의 상관관계 출력
sns.pairplot(crime_anal_norm, x_vars=["인구수", "CCTV"], y_vars=["살인검거율", "강도검거율"], kind='reg', size=3)
plt.show()  #결과 : 살인 및 폭력 검거율과 CCTV의 관계가 음의 관계?

#검거율의 합계인 검거 항목 최고값을 100으로 한정하고 정
tmp_max = crime_anal_norm['검거'].max()
crime_anal_norm['검거'] = crime_anal_norm['검거'] / tmp_max * 100
crime_anal_norm_sort = crime_anal_norm.sort_values(by='검거', ascending=False)
print(crime_anal_norm_sort.head())

#검거율 경향
target_col = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']
plt.figure(figsize=(10,10))
sns.heatmap(crime_anal_norm_sort[target_col], annot=True, fmt='f', linewidths=.5)
plt.title('범죄 검거 비율 (정규화된 검거의 합으로 정렬)')
plt.show()  #결과 : 절도검거율이 가장 낮다. 검거율 높은구, 낮은구 확인

#발생 건수의 합으로 정렬해서 heatmap으로 출력
target_col = ['강간', '강도', '살인', '절도', '폭력', '범죄']
crime_anal_norm['범죄'] = crime_anal_norm['범죄'] / 5
crime_anal_norm_sort = crime_anal_norm.sort_values(by='범죄', ascending=False)
plt.figure(figsize=(10,10))
sns.heatmap(crime_anal_norm_sort[target_col], annot=True, fmt='f', linewidths=.5)
plt.title('범죄비율 (정규화된 발생 건수로 정렬)')
plt.show()  #결과 : 범죄 발생 건수가 높은, 낮은 지역 확인

crime_anal_norm.to_csv('02. crime_in_Seoul_final.csv', sep=',', encoding='utf-8')

#경계선 json파일
import json
import folium
geo_path = '02. skorea_municipalities_geo_simple.json'
geo_str = json.load(open(geo_path, encoding='utf-8'))

#지도 위치 지정
map = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')
#살인 발생 건수로 컬러맵 지정, fill_color옵션 PuRd, PuRd, YlGnBu
map.choropleth(geo_data = geo_str, data= crime_anal_norm['살인'], 
               columns = [crime_anal_norm.index, crime_anal_norm['살인']], 
               fill_color = 'PuRd', key_on = 'feature.id')
map.save('map5_1.html')

#지도 위치 지정
map = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')
#강간 발생 건수로 컬러맵 지정
map.choropleth(geo_data = geo_str, data= crime_anal_norm['강간'], 
               columns = [crime_anal_norm.index, crime_anal_norm['강간']], 
               fill_color = 'PuRd', key_on = 'feature.id')
map.save('map5_2.html')

#지도 위치 지정
map = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')
#강간 발생 건수로 컬러맵 지정
map.choropleth(geo_data = geo_str, data= crime_anal_norm['범죄'], 
               columns = [crime_anal_norm.index, crime_anal_norm['범죄']], 
               fill_color = 'PuRd', key_on = 'feature.id')
map.save('map5_3.html') #결과 : 강남3구, 강서구 주변의 범죄 건수가 높은것을 확인

#인구 대비 범죄 발생 비율
tmp_criminal = crime_anal_norm['살인'] / crime_anal_norm['인구수'] * 1000000
map = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')
map.choropleth(geo_data = geo_str, data= tmp_criminal, 
               columns = [crime_anal_norm.index, tmp_criminal], 
               fill_color = 'PuRd', key_on = 'feature.id', legend_name='Criminal Rate (%)')
map.save('map5_4.html') #결과 : 강남3구가 1위는 아니지만 안전도가 제일 높은것은 아니다.
                        #중구, 종로구의 범죄율이 엄청 높아짐. 거주 인구가 적고, 관광지여서 라고 추측

#위도, 경도, 검거율 입력
crime_anal_raw['lat'] = station_lat
crime_anal_raw['lng'] = station_lng
col = ['살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거']
tmp = crime_anal_raw[col] / crime_anal_raw[col].max()
crime_anal_raw['검거'] = np.sum(tmp, axis=1)
print(crime_anal_raw.head())

#경찰서 위치를 맵에 표시
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)
for n in crime_anal_raw.index:
    folium.Marker([crime_anal_raw['lat'][n], crime_anal_raw['lng'][n]]).add_to(map)
map.save('map6.html')

#경찰서의 검거율 및 범죄에 대한 방어력 (원이 클수록 검거율이 높다)
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)
for n in crime_anal_raw.index:
    folium.CircleMarker([crime_anal_raw['lat'][n], crime_anal_raw['lng'][n]], 
                        radius= crime_anal_raw['검거'][n]*10, 
                        color='#3186cc', fill_color='#3186cc').add_to(map)
map.save('map7.html')

#범죄율, 검거율 표시
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)
map.choropleth(geo_data = geo_str, data= crime_anal_norm['범죄'], 
               columns = [crime_anal_norm.index, crime_anal_norm['범죄']], 
               fill_color = 'PuRd', key_on = 'feature.id', legend_name='Criminal Rate (%)')
for n in crime_anal_raw.index:
    folium.CircleMarker([crime_anal_raw['lat'][n], crime_anal_raw['lng'][n]], 
                        radius= crime_anal_raw['검거'][n]*10, 
                        color='#3186cc', fill_color='#3186cc').add_to(map)
    folium.Marker([crime_anal_raw['lat'][n], crime_anal_raw['lng'][n]]).add_to(map)
map.save('map8.html')
#결과 : 서울 서부는 범죄는 많이 발생하지만 방어력 또한 높다.
#       서울 강북의 중앙부는 경찰서의 검거율도 높지 않지만, 범죄 발생 건수도 높지 않다.
