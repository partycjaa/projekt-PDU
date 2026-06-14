import pandas as pd
import zipfile



sciezka_zip = r"C:\Users\Robert\Desktop\IAD\projektpdu\2017-citibike-tripdata.zip"
lista_df = []

with zipfile.ZipFile(sciezka_zip, 'r') as archiwum:
    wszystkie_pliki = archiwum.namelist()
    
    pliki_csv = [plik for plik in wszystkie_pliki if plik.endswith('.csv') and '__MACOSX' not in plik]
    
    
    for plik_csv in pliki_csv:
        print(f"Wczytywanie: {plik_csv}")
        with archiwum.open(plik_csv) as f:
            df_tymczasowe = pd.read_csv(f)
            lista_df.append(df_tymczasowe)

print("Łączenie danych...")
df2017 = pd.concat(lista_df, ignore_index=True)

print(df2017.info())

df2017.to_parquet(r"C:\Users\Robert\Desktop\IAD\projektpdu\citi_bike_2017_gotowy.parquet", compression='snappy')
print("Plik 2017 zapisany")

#-----------------------------------------------------------------------------

sciezka_zip = r"C:\Users\Robert\Desktop\IAD\projektpdu\2018-citibike-tripdata.zip"
lista_df = []

with zipfile.ZipFile(sciezka_zip, 'r') as archiwum:
    wszystkie_pliki = archiwum.namelist()
    
    pliki_csv = [plik for plik in wszystkie_pliki if plik.endswith('.csv') and '__MACOSX' not in plik]
    
    
    for plik_csv in pliki_csv:
        print(f"Wczytywanie: {plik_csv}")
        with archiwum.open(plik_csv) as f:
            df_tymczasowe = pd.read_csv(f)
            lista_df.append(df_tymczasowe)

print("Łączenie danych...")
df2018 = pd.concat(lista_df, ignore_index=True)

print(df2018.info())

df2017.to_parquet(r"C:\Users\Robert\Desktop\IAD\projektpdu\citi_bike_2018_gotowy.parquet", compression='snappy')
print("Plik 2018 zapisany")

