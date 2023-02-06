import pandas as pd
import numpy as np
import streamlit as st 
import matplotlib.pyplot as plt
import folium
from folium import plugins
from streamlit_folium import st_folium
from streamlit_echarts import st_echarts
from streamlit_option_menu import option_menu
import json
import requests
from bs4 import BeautifulSoup
from st_aggrid import AgGrid

df = pd.read_csv('katalog_gempa.csv', sep=',')
df = df[['tgl','ot','lat', 'lon','depth', 'mag','remark']]

satu = []
dua = []
tiga = []
empat = []
lima = []
enam = []
for i in range (len(df['mag'])) :
    # print(df['mag'][i])
    if df['mag'][i] <= 2.4 : 
        satu.append(df.iloc[i].to_list())
    elif df['mag'][i] >= 2.5 and df['mag'][i] <= 5.4 :
        dua.append(df.iloc[i].to_list())
    elif df['mag'][i] >= 5.5 and df['mag'][i] <= 6.0 :
        tiga.append(df.iloc[i].to_list())
    elif df['mag'][i] >= 6.1 and df['mag'][i] <= 6.9 :
        empat.append(df.iloc[i].to_list())
    elif df['mag'][i] >= 7.0 and df['mag'][i] <= 7.9 :
        lima.append(df.iloc[i].to_list())
    elif df['mag'][i] >= 8.0 :
        enam.append(df.iloc[i].to_list())


dataset = pd.read_csv('katalog_gempa.csv', sep=',')
dataset.drop(['strike1', 'dip1', 'rake1', 'strike2', 'dip2', 'rake2'], axis=1, inplace=True)

st.set_page_config(
    page_title="Data Gempa", 
    page_icon=":tada:",
    layout="wide",
)

st.markdown("""
        <style>
            .reportview-container .main .block-container{
                background-color: blue;
            }
        </style>
        """, unsafe_allow_html=True)
# st.sidebar.header("Menu")
selected = option_menu(
    menu_title = None,
    orientation = "horizontal",
    default_index = 0,
    options = [
        'Home','Kekuatan Gempa','Jumlah Gempa',
        'Lokasi Gempa','Peta Gempa','Skala Gempa'],
    icons=["house","bar-chart-steps","graph-up","geo-fill","geo-alt","sort-numeric-up-alt"]
)

# st.title("Contoh Merubah Tampilan di Streamlit")
# st.header("Header")
# st.subheader("Subheader")
st.set_option('deprecation.showPyplotGlobalUse', False)


if selected == 'Home' or selected == '':
    st.subheader("Gempabumi")
    st.title("Gempabumi Terkini")
    url = ("https://www.bmkg.go.id/gempabumi-dirasakan.html")
    req = requests.get(url)
    soup = BeautifulSoup(req.text)
    table = soup.find_all('tr')
    judul = []
    for row in table : 
        cols = row.find_all('th')
        judul.append([col.text.strip() for col in cols])
        if (len(judul)) == 1 : 
            break

    judul = judul[0]
    del judul[0]
    judul.append("Terdampak")
    # print(judul)

    datas = []
    for row in table : 
        cols = row.find_all('td')
        datas.append([col.text.strip() for col in cols])

    del datas[0]
    pusat = []
    for i in range (len(datas)) :
        del datas[i][0]
        kalimat = datas[i][4]
        index = kalimat.find("\n\n\n\n\n×")
        new_string = kalimat[:index]
        datas[i][4] = new_string
        # print(datas[i])

    mmi = []
    for i in range (len(datas)) : 
        pusat = datas[i][4].split("\n")
        datas[i][4] = pusat[0]
        print(datas[i][4])
        del pusat[0]
        mmi.append(pusat)

    for i in range (len(datas)) : 
        datas[i].extend([mmi[i]])

    # datas
    df = pd.DataFrame(datas, columns=judul)
    AgGrid(df)
    
    st.write("[Source >](https://www.bmkg.go.id/gempabumi-dirasakan.html)")

elif selected == 'Kekuatan Gempa' :
    st.write("""# Rata- rata Kekuatan Gempa""")
    # Mengambil dataset hanya dari tahun 2022
    df = pd.read_csv('katalog_gempa.csv', index_col='tgl', parse_dates=True)
    dataset2022 = df['2022']

    # Menampilkan kekuatan rata-rata setiap wilayah pada tahun 2022
    ratarata = dataset2022.groupby(['remark'])[['mag']].mean()
    ratarata.get('remark')

    # Menampilkan 10 wilayah dengan kekuatan rata-rata paling besar
    magUrut = ratarata.sort_values('mag',ascending=True)
    magUrut10 = magUrut.tail(10)

    magUrut10.reset_index(drop=False, inplace=True)
    plt.barh(magUrut10['remark'], magUrut10['mag'], color='#c86558')

    plt.title('Rata-rata Kekuatan Gempa Terbesar Pada Tahun 2022', size=18)
    plt.xlabel('\nMagnitudo')
    plt.ylabel('Wilayah\n')
    plt.xticks()
    plt.yticks()
    st.pyplot()

elif selected == 'Jumlah Gempa' :
    st.write("""# Jumlah Gempa per Tahun""") #menampilkan halaman utama
    year = pd.DataFrame(dataset['tgl'].str[0:4])
    x = year.loc[:,'tgl']
    l = list(x)
    count = [l.count('2008'),l.count('2009'),l.count('2010'),l.count('2011'),
            l.count('2012'),l.count('2013'),l.count('2014'),l.count('2015'),
            l.count('2016'),l.count('2017'),l.count('2018'),l.count('2019'),
            l.count('2020'),l.count('2021'),l.count('2022'),l.count('2023')]

    gempa_tahun =  pd.DataFrame(dataset['tgl'].str[0:4]).drop_duplicates()
    gempa_tahun['count'] = count
    # display(gempa_tahun)


    plt.plot(gempa_tahun['tgl'], gempa_tahun['count'])
    plt.xlabel("Tahun")
    plt.ylabel("Jumlah Gempa Pertahun")
    plt.title("Jumlah Gempa Yang Terjadi Pertahun")
    plt.xticks(rotation = 45) 
    st.pyplot()
elif selected == 'Lokasi Gempa' :
    st.write("""# Lokasi Yang Sering Terjadi Gempa""") #menampilkan halaman utama
    wilayah = dataset['remark'].unique()
    count = {}

    for i in wilayah :
        count[i] = 0

    for i in dataset['remark'] :
        count[i] += 1   

    daerah = []
    jumlah_gempa = []
    sorted_marks = sorted(count.items(), key=lambda x: x[1])
    for i in range(len(sorted_marks)) :
        daerah.append(sorted_marks[i][0])
        jumlah_gempa.append(sorted_marks[i][1])

    data = {'Wilayah' : list(reversed(daerah)),
            'Gempa yang Terjadi' : list(reversed(jumlah_gempa))}
    df = pd.DataFrame(data)
    # st.dataframe(df.head(5))

    # Visualisasi lokasi yang sering terjadi gempa
    daerah_terbanyak = []
    gempa_terbanyak = []
    for i in range(len(df.head())) :
        daerah_terbanyak.append(df['Wilayah'][i])
        gempa_terbanyak.append(df['Gempa yang Terjadi'][i])

    jumlah = 0
    for i in range(5, 51) :
        jumlah += df['Gempa yang Terjadi'][i]

    daerah_terbanyak.append('Other')
    gempa_terbanyak.append(jumlah)

    def func(pct, allvalues):
        absolute = int(pct / 100.*np.sum(allvalues))
        return "{:.1f}%\n({:d})".format(pct, absolute)

    plt.figure(figsize = (9, 9))
    plt.pie(gempa_terbanyak,
            labels = daerah_terbanyak,
            autopct = lambda pct: func(pct, gempa_terbanyak))
    plt.title("5 Wilayah yang Sering Terjadi Gempa")
    st.pyplot()

    result = []
    for i in range (len(gempa_terbanyak)) : 
        result.append({"value" : gempa_terbanyak[i], "name": daerah_terbanyak[i]})

    cek = [
                {"value": 9433, "name": "Minahassa Peninsula - Sulawesi"},
                {"value": 7897, "name": "Sulawesi - Indonesia"},
                {"value": 7312, "name": "Sumbawa Region - Indonesia"},
                {"value": 6798, "name": "Java - Indonesia"},
                {"value": 5941, "name": "Northern Sumatra - Indonesia"},
                {"value": 55506, "name": "Other"},
            ]
    
    apa = json.dumps(cek, default=str)

    # st.write(type(apa))

    options = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "1%", "left": "center"},
    "series": [
        {
            "name": "Lokasi Gempa",
            "type": "pie",
            "radius": ["50%", "70%"],
            "avoidLabelOverlap": False,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#fff",
                "borderWidth": 2,
            },
            "label": {"show": False, "position": "center"},
            "emphasis": {
                "label": {"show": True, "fontSize": "15", "fontWeight": "bold"}
            },
            "labelLine": {"show": False},
            "data": [
                {"value": 9433, "name": "Minahassa Peninsula - Sulawesi"},
                {"value": 7897, "name": "Sulawesi - Indonesia"},
                {"value": 7312, "name": "Sumbawa Region - Indonesia"},
                {"value": 6798, "name": "Java - Indonesia"},
                {"value": 5941, "name": "Northern Sumatra - Indonesia"},
                {"value": 55506, "name": "Other"},
            ],
        }
    ],
    }
    st_echarts(
        options=options, height="500px",
    )

elif selected == 'Peta Gempa' :
    st.title("Peta Sebaran Jumlah Gempa di Indonesia")
    rome_lat, rome_lng = -4.445604, 119.807565    
    # init the folium map object
    my_map = folium.Map(location=[rome_lat, rome_lng], zoom_start=5, width=2000, height=1000)
    # add all the point from the file to the map object using FastMarkerCluster
    my_map.add_child(plugins.FastMarkerCluster(dataset[['lat', 'lon']].values.tolist()))

    st_folium(my_map)
elif selected == 'Skala Gempa' :
    with st.container() : 
        
        st.subheader("Daftar Gempa (< 2.4)") 
        st.write("Biasanya tidak terasa, tetapi dapat direkam dengan seismograf")
        df = pd.DataFrame(satu, columns=["Tanggal","Jam","Latitude","Longitude","Kedalaman","Magnitudo","Lokasi"], dtype=str)
        st.dataframe(df)

    with st.container() : 
        
        st.subheader("Daftar Gempa (2.5 - 5,4)") 
        st.write("Sering dirasakan, tetapi hanya menyebabkan kerusakan kecil")
        df = pd.DataFrame(dua, columns=["Tanggal","Jam","Latitude","Longitude","Kedalaman","Magnitudo","Lokasi"], dtype=str)
        st.dataframe(df)

    with st.container() : 
        
        st.subheader("Daftar Gempa (5,5 - 6,0)") 
        st.write("Dapat menyebabkan kerusakan ringan pada bangunan dan struktur lainnya")
        df = pd.DataFrame(tiga, columns=["Tanggal","Jam","Latitude","Longitude","Kedalaman","Magnitudo","Lokasi"], dtype=str)
        st.dataframe(df)

    with st.container() : 
        
        st.subheader("Daftar Gempa (6,1 - 6,9)") 
        st.write("Dapat menyebabkan banyak kerusakan di daerah berpenduduk padat")
        df = pd.DataFrame(empat, columns=["Tanggal","Jam","Latitude","Longitude","Kedalaman","Magnitudo","Lokasi"], dtype=str)
        st.dataframe(df)

    with st.container() : 
        
        st.subheader("Daftar Gempa (7,0 - 7,9)") 
        st.write("Gempa bumi besar dengan kerusakan serius")
        df = pd.DataFrame(lima, columns=["Tanggal","Jam","Latitude","Longitude","Kedalaman","Magnitudo","Lokasi"], dtype=str)
        st.dataframe(df)














