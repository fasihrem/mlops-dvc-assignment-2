import pandas as pd
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("raw_data.csv")

df.dropna(inplace=True)

scaler = StandardScaler()
df[["Temperature", "WindSpeed"]] = scaler.fit_transform(df[["Temperature", "WindSpeed"]])

df.to_csv("processed_data.csv", index=False)
print("Processed data saved to processed_data.csv")