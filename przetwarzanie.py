import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import gc
import matplotlib.ticker as ticker

sns.set_theme(style="whitegrid")

# nowe i stare nazwy
mapowanie = {
    'tripduration': 'trip_duration', 'trip duration': 'trip_duration',
    'starttime': 'start_time', 'start time': 'start_time',
    'start station id': 'start_station_id', 'start station latitude': 'start_station_latitude',
    'start station longitude': 'start_station_longitude', 'end station id': 'end_station_id',
    'end station latitude': 'end_station_latitude', 'end station longitude': 'end_station_longitude',
    'usertype': 'user_type', 'user type': 'user_type', 'birth year': 'birth_year'
}

def napraw_kolumny(df):
    df.columns = df.columns.str.lower()
    df = df.rename(columns=mapowanie)
    if df.columns.has_duplicates:
        nowe_kolumny = {}
        for kolumna in df.columns.unique():
            dane = df[kolumna]
            if isinstance(dane, pd.DataFrame):
                scalona = dane.iloc[:, 0]
                for i in range(1, dane.shape[1]):
                    scalona = scalona.combine_first(dane.iloc[:, i])
                nowe_kolumny[kolumna] = scalona
            else:
                nowe_kolumny[kolumna] = dane
        df = pd.DataFrame(nowe_kolumny)
    return df


# liczenie dystansu po wspolrzednych

def haversine_vectorize(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    a = np.sin((lat2 - lat1)/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1)/2)**2
    return 2 * np.arcsin(np.sqrt(a)) * 6371

# PRZETWARZANIE

# podsumowania z każdego miesiąca
podsumowanie_przejazdow = []
podsumowanie_dystansu = []
podsumowanie_uzytkownikow = []
wszystkie_dystanse = [] # lista wartości dystansów do boxplota 

pliki_do_przetworzenia = [
    (r"C:\Users\Robert\Desktop\IAD\projektpdu\citi_bike_2017_gotowy.parquet", 2017), 
    (r"C:\Users\Robert\Desktop\IAD\projektpdu\citi_bike_2018_gotowy.parquet", 2018)
]

for sciezka, rok in pliki_do_przetworzenia:
    print(f"\n--- Przetwarzanie roku {rok} ---")
    
   
    df = pd.read_parquet(sciezka)
    df = napraw_kolumny(df)
    
    #dodajemy rok i miesiąc żeby ramu nie wywalilo
    df['year'] = rok
    df['start_time'] = pd.to_datetime(df['start_time'], format='mixed', errors='coerce')
    df['month'] = df['start_time'].dt.month
    


    # czyszczenie anomalii
    print("Czyszczenie anomalii...")
    df['trip_duration'] = pd.to_numeric(df['trip_duration'], errors='coerce')
    df['birth_year'] = pd.to_numeric(df['birth_year'], errors='coerce')
    
    df = df[(df['trip_duration'] >= 60) & (df['trip_duration'] <= 10800)]  # tylko przejazdy powyzej 1 minuty i ponizej 3 godzin
    

    df['age'] = df['year'] - df['birth_year']
    df = df[df['age'].isna() | ((df['age'] >= 16) & (df['age'] <= 90))]  # osoby w wieku od 16 do 90 lat

    df = df[df['start_station_id'] != df['end_station_id']]  # brak przejazdow w kolko, tzn zaczynamy i konczymy w tej samej stacji
    
  
    #  agregacja danych
    print("Agregowanie statystyk")
    
    #Zliczenie przejazdów w miesiącach
    liczba_miesiecznie = df.groupby('month').size().reset_index(name='count')
    liczba_miesiecznie['year'] = rok
    podsumowanie_przejazdow.append(liczba_miesiecznie)
    
    #Obliczanie dystansu i uśrednianie w miesiącach
    df['distance_km'] = haversine_vectorize(
        df['start_station_longitude'], df['start_station_latitude'],
        df['end_station_longitude'], df['end_station_latitude']
    )
    dystans_miesiecznie = df.groupby('month')['distance_km'].mean().reset_index()
    dystans_miesiecznie['year'] = rok
    podsumowanie_dystansu.append(dystans_miesiecznie)
    
    #dystanse do Boxplota
    dystanse_surowe = df[['year', 'distance_km']].copy()
    wszystkie_dystanse.append(dystanse_surowe)
    
    #Zliczenie użytkowników
    uzytkownicy = df.groupby('user_type').size().reset_index(name='count')
    uzytkownicy['year'] = rok
    podsumowanie_uzytkownikow.append(uzytkownicy)
    
    #Czyszczenie Ramu
    print(f"Zakończono {rok}. Czyszczenie ramu")
    del df
    gc.collect()


#SCALANIE WYNIKÓW

print("\nPrzygotowanie wykresów")
df_przejazdy = pd.concat(podsumowanie_przejazdow, ignore_index=True)
df_sredni_dystans = pd.concat(podsumowanie_dystansu, ignore_index=True)
df_uzytkownicy = pd.concat(podsumowanie_uzytkownikow, ignore_index=True)
df_box_dystans = pd.concat(wszystkie_dystanse, ignore_index=True)



#GENEROWANIE WYKRESÓW

plt.figure(figsize=(18, 12))

# zamiana notacji wykladniczej na mln
def format_mln(x, pos):
    return f'{x*1e-6:g} mln'

#WYKRES 1: Liczba przejazdów
ax1 = plt.subplot(2, 2, 1)
sns.lineplot(data=df_przejazdy, x='month', y='count', hue='year', marker='o', palette=['#1f77b4', '#ff7f0e'])
plt.title('Liczba przejazdów w poszczególnych miesiącach (2017 vs 2018)', fontsize=14)
plt.xlabel('Miesiąc')
plt.ylabel('Liczba przejazdów')
plt.xticks(range(1, 13))
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_mln))

#WYKRES 2: Średni dystans
plt.subplot(2, 2, 2)
sns.lineplot(data=df_sredni_dystans, x='month', y='distance_km', hue='year', marker='s', palette=['#1f77b4', '#ff7f0e'])
plt.title('Średni dystans w linii prostej między stacjami (km)', fontsize=14)
plt.xlabel('Miesiąc')
plt.ylabel('Dystans (km)')
plt.xticks(range(1, 13))

#WYKRES 3: Rozkład dystansów (Boxplot)
plt.subplot(2, 2, 3)
sns.boxplot(data=df_box_dystans, x='year', y='distance_km', hue='year', palette=['#1f77b4', '#ff7f0e'], showfliers=False, legend=False)
plt.title('Rozkład pokonywanego dystansu', fontsize=14)
plt.xlabel('Rok')
plt.ylabel('Dystans (km)')

#WYKRES 4: Użytkownicy
ax4 = plt.subplot(2, 2, 4)
sns.barplot(data=df_uzytkownicy, x='user_type', y='count', hue='year', palette=['#1f77b4', '#ff7f0e'])
plt.title('Struktura użytkowników w latach', fontsize=14)
plt.xlabel('Typ użytkownika')
plt.ylabel('Liczba przejazdów')
ax4.yaxis.set_major_formatter(ticker.FuncFormatter(format_mln))

plt.tight_layout()
plt.show()