import pandas as pd

df2017 = pd.read_parquet(r"C:\Users\Robert\Desktop\IAD\projektpdu\citi_bike_2017_gotowy.parquet")
df2018 = pd.read_parquet(r"C:\Users\Robert\Desktop\IAD\projektpdu\citi_bike_2018_gotowy.parquet")

print(df2018.columns)