import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import gc

sns.set_theme(style="whitegrid")

# ==========================================
# 1. WCZYTANIE DANYCH
# ==========================================
print("Wczytywanie danych...")
df2017 = pd.read_parquet(r"C:\Users\Robert\Desktop\IAD\projektpdu\citi_bike_2017_gotowy.parquet")
df2018 = pd.read_parquet(r"C:\Users\Robert\Desktop\IAD\projektpdu\citi_bike_2018_gotowy.parquet")

# --- TYMCZASOWE ZABEZPIECZENIE PRZED ZAWIESZANIEM VS CODE ---
# Używamy tylko 5% wierszy. Dzięki temu cały kod wykona się w 2 sekundy.
df2017 = df2017.sample(frac=0.05, random_state=42)
df2018 = df2018.sample(frac=0.05, random_state=42)# ==========================================
# 2. NAPRAWA I UJEDNOLICENIE KOLUMN
# ==========================================
# Słownik przekształcający każdą wariację na jeden, spójny standard z podkreśleniami
mapowanie = {
    'tripduration': 'trip_duration',
    'trip duration': 'trip_duration',
    'starttime': 'start_time',
    'start time': 'start_time',
    'stoptime': 'stop_time',
    'stop time': 'stop_time',
    'start station id': 'start_station_id',
    'start station name': 'start_station_name',
    'start station latitude': 'start_station_latitude',
    'start station longitude': 'start_station_longitude',
    'end station id': 'end_station_id',
    'end station name': 'end_station_name',
    'end station latitude': 'end_station_latitude',
    'end station longitude': 'end_station_longitude',
    'bikeid': 'bike_id',
    'bike id': 'bike_id',
    'usertype': 'user_type',
    'user type': 'user_type',
    'birth year': 'birth_year',
    'gender': 'gender'
}

def napraw_kolumny(df):
    # Krok A: Zmiana wszystkich wielkich liter na małe
    df.columns = df.columns.str.lower()
    
    # Krok B: Przemianowanie kolumn według słownika mapującego
    df = df.rename(columns=mapowanie)
    
    # Krok C: Optymalne scalanie zduplikowanych kolumn (bez obciążania RAMu)
    if df.columns.has_duplicates:
        nowe_kolumny = {}
        for kolumna in df.columns.unique():
            dane = df[kolumna]
            if isinstance(dane, pd.DataFrame):
                # Bierzemy pierwszą kolumnę z duplikatów
                scalona = dane.iloc[:, 0]
                # Uzupełniamy ją danymi z kolejnych (bardzo szybka operacja)
                for i in range(1, dane.shape[1]):
                    scalona = scalona.combine_first(dane.iloc[:, i])
                nowe_kolumny[kolumna] = scalona
            else:
                nowe_kolumny[kolumna] = dane
        df = pd.DataFrame(nowe_kolumny)
        
    return df

print("Naprawianie struktury kolumn...")
df2017 = napraw_kolumny(df2017)
df2018 = napraw_kolumny(df2018)

# Dodanie informacji o roku i ostateczne scalenie obu roczników
df2017['year'] = 2017
df2018['year'] = 2018
df = pd.concat([df2017, df2018], ignore_index=True)
df = df.sample(frac=0.05, random_state=42)
del df2017
del df2018
gc.collect()

# Sprawdzenie efektu
print("\nOstateczne nazwy kolumn po naprawie:")
print(df.columns.tolist())

# ==========================================
# 3. CZYSZCZENIE DANYCH (Teraz 'trip_duration' zadziała)
# ==========================================
print("\nRozmiar przed czyszczeniem:", len(df))

# Konwersja kolumn numerycznych (Pandas czasami wczytuje je jako tekst przy bałaganie w typach)
df['trip_duration'] = pd.to_numeric(df['trip_duration'], errors='coerce')
df['birth_year'] = pd.to_numeric(df['birth_year'], errors='coerce')

# Filtrowanie anomalii czasowych
df = df[df['trip_duration'] >= 60]
df = df[df['trip_duration'] <= 10800]

# Odrzucenie błędnych dat urodzenia i obliczenie wieku
df = df.dropna(subset=['birth_year'])
df['age'] = df['year'] - df['birth_year']
df = df[(df['age'] >= 16) & (df['age'] <= 90)]

# Wykluczenie przejazdów w ramach tej samej stacji
df = df[df['start_station_id'] != df['end_station_id']]

print("Rozmiar po czyszczeniu:", len(df))

# ==========================================
# 4. INŻYNIERIA CECH (OBLICZANIE DYSTANSU)
# ==========================================
# Funkcja Haversine do obliczenia odległości w linii prostej (w kilometrach) pomiędzy stacjami
def haversine_vectorize(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    r = 6371 # Promień Ziemi w kilometrach
    return c * r

print("Obliczanie dystansów...")
df['distance_km'] = haversine_vectorize(
    df['start_station_longitude'], df['start_station_latitude'],
    df['end_station_longitude'], df['end_station_latitude']
)

# Konwersja czasu na format datetime i wyciągnięcie miesiąca
df['start_time'] = pd.to_datetime(df['start_time'], format='mixed', errors='coerce')
df['month'] = df['start_time'].dt.month

# ==========================================
# 5. ANALIZA WIZUALNA (HIPOTEZY)
# ==========================================
print("Generowanie wykresów...")
plt.figure(figsize=(18, 12))

# --- WYKRES 1: Liczba przejazdów w miesiącach (2017 vs 2018) ---
# Czy integracja z Lyft zwiększyła całkowitą liczbę użytkowników?
plt.subplot(2, 2, 1)
monthly_counts = df.groupby(['year', 'month']).size().reset_index(name='count')
sns.lineplot(data=monthly_counts, x='month', y='count', hue='year', marker='o', palette=['#1f77b4', '#ff7f0e'])
plt.title('Liczba przejazdów w poszczególnych miesiącach (2017 vs 2018)', fontsize=14)
plt.xlabel('Miesiąc')
plt.ylabel('Liczba przejazdów')
plt.xticks(range(1, 13))

# --- WYKRES 2: Średni dystans przejazdu ---
# E-biki zwiększyły zasięg. Czy to widać w dystansie pomiędzy stacjami w 2018 r.?
plt.subplot(2, 2, 2)
monthly_dist = df.groupby(['year', 'month'])['distance_km'].mean().reset_index()
sns.lineplot(data=monthly_dist, x='month', y='distance_km', hue='year', marker='s', palette=['#1f77b4', '#ff7f0e'])
plt.title('Średni dystans w linii prostej między stacjami (km)', fontsize=14)
plt.xlabel('Miesiąc')
plt.ylabel('Dystans (km)')
plt.xticks(range(1, 13))

# --- WYKRES 3: Rozkład dystansów (Boxplot) ---
plt.subplot(2, 2, 3)
# Dodano hue='year' oraz legend=False zgodnie z zaleceniem z ostrzeżenia Seaborn
sns.boxplot(data=df, x='year', y='distance_km', hue='year', palette=['#1f77b4', '#ff7f0e'], showfliers=False, legend=False)
plt.title('Rozkład pokonywanego dystansu', fontsize=14)
plt.xlabel('Rok')
plt.ylabel('Dystans (km)')

# --- WYKRES 4: Użytkownicy - Subscriber (Abonament) vs Customer (Jednorazowy) ---
# Poprawiono 'usertype' na 'user_type'
plt.subplot(2, 2, 4)
user_dist = df.groupby(['year', 'user_type']).size().reset_index(name='count')
sns.barplot(data=user_dist, x='user_type', y='count', hue='year', palette=['#1f77b4', '#ff7f0e'])
plt.title('Struktura użytkowników w latach', fontsize=14)
plt.xlabel('Typ użytkownika')
plt.ylabel('Liczba przejazdów')

plt.tight_layout()
plt.show()