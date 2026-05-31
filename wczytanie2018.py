import pandas as pd
import zipfile



sciezka_zip = r"C:\Users\Robert\Desktop\IAD\projektpdu\2018-citibike-tripdata.zip"
lista_df = []

with zipfile.ZipFile(sciezka_zip, 'r') as archiwum:
    # Pobieramy listę wszystkich plików wewnątrz archiwum
    wszystkie_pliki = archiwum.namelist()
    
    # Filtrujemy listę: wybieramy tylko pliki kończące się na '.csv' 
    # oraz pomijamy ukryte foldery systemowe macOS ('__MACOSX')
    pliki_csv = [plik for plik in wszystkie_pliki if plik.endswith('.csv') and '__MACOSX' not in plik]
    
    print(f"Znaleziono {len(pliki_csv)} plików CSV. Rozpoczynam wczytywanie...")
    
    # Iterujemy po przefiltrowanej liście
    for plik_csv in pliki_csv:
        print(f"Wczytywanie: {plik_csv}")
        # Otwieramy pojedynczy plik CSV z wnętrza ZIP-a
        with archiwum.open(plik_csv) as f:
            # Wczytujemy do Pandas
            df_tymczasowe = pd.read_csv(f)
            lista_df.append(df_tymczasowe)

print("Łączenie danych...")
# Łączymy wszystkie wczytane ramki w jedną wielką ramkę df2017
df2017 = pd.concat(lista_df, ignore_index=True)

print("Gotowe!")
print(df2017.info())

df2017.to_parquet(r"C:\Users\Robert\Desktop\IAD\projektpdu\citi_bike_2018_gotowy.parquet", compression='snappy')
print("Plik pośredni został zapisany!")

