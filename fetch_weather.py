import requests
import csv
import os
from datetime import datetime

API_KEY = os.getenv("OWM_API_KEY")
CITY = "London"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

CSV_FILE = "raw_data.csv"

def fetch_weather():
    response = requests.get(URL)
    data = response.json()

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    weather_data = {
        "DateTime": timestamp,
        "Temperature": data["main"]["temp"],
        "Humidity": data["main"]["humidity"],
        "WindSpeed": data["wind"]["speed"],
        "Condition": data["weather"][0]["description"]
    }

    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=weather_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(weather_data)

    print("Weather data saved:", weather_data)

if __name__ == "__main__":
    fetch_weather()