import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
import os
import joblib
# import matplotlib.pyplot as plt
# import seaborn as sns

model_filename = "../models/model.pkl"

# Load your data
df = pd.read_csv('../data/preprocessed_data.csv')  # Replace with your actual file path

# Drop rows with missing values
df = df.dropna(subset=['temperature', 'humidity', 'wind_speed', 'weather_condition'])

# Encode categorical variable
encoder = OneHotEncoder(sparse_output=False, drop='first')
encoded_conditions = encoder.fit_transform(df[['weather_condition']])
condition_df = pd.DataFrame(encoded_conditions, columns=encoder.get_feature_names_out(['weather_condition']))

# Concatenate encoded features with the original dataframe
df = pd.concat([df.reset_index(drop=True), condition_df], axis=1)

# Define features (X) and target (y)
X = df[['humidity', 'wind_speed'] + list(condition_df.columns)]
y = df['temperature']

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit the model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
print("Mean Squared Error:", mean_squared_error(y_test, y_pred))
print("R² Score:", r2_score(y_test, y_pred))

if os.path.exists(model_filename):
    os.remove(model_filename)

# Save the trained model
joblib.dump(model, model_filename)
print("model saved as pkl")