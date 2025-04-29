import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


data = pd.read_csv("../data/raw_data.csv", sep=",")
# print(data.head())

print(data.columns)

data = data.dropna(subset=['temperature', 'humidity', 'wind_speed'])

data['weather_condition'] = data['weather_condition'].fillna('Unknown')
data['weather_description'] = data['weather_description'].fillna('No description')
data['city'] = data['city'].fillna('Unknown')
data['data_type'] = data['data_type'].fillna('Unknown')

scaler = MinMaxScaler()
numeric_cols = ['temperature', 'humidity', 'wind_speed']
data[numeric_cols] = scaler.fit_transform(data[numeric_cols])

data.to_csv('../data/preprocessed_data.csv', index=False)
print("data processed and saved to new csv")