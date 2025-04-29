import requests
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import time
import argparse
import random

def get_current_weather(api_key, city, units="metric"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units={units}&appid={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        data = response.json()
        
        # Extract required weather information
        weather_data = {
            'date_time': datetime.fromtimestamp(data['dt']),
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'weather_condition': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'city': city,
            'data_type': 'current'
        }
        
        return weather_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching current weather data: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_forecast_weather(api_key, city, units="metric"):
    """
    Get 5-day forecast weather data for a specific city with 3-hour intervals.
    
    Parameters:
    - api_key: OpenWeatherMap API key
    - city: City name (e.g., "London,UK")
    - units: Units of measurement ("metric", "imperial", or "standard")
    
    Returns:
    - List of dictionaries containing weather data or empty list if request fails
    """
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units={units}&appid={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        data = response.json()
        
        # Extract required weather information for each forecast time
        forecast_data = []
        
        for item in data['list']:
            weather_info = {
                'date_time': datetime.fromtimestamp(item['dt']),
                'temperature': item['main']['temp'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed'],
                'weather_condition': item['weather'][0]['main'],
                'weather_description': item['weather'][0]['description'],
                'city': city,
                'data_type': 'forecast'
            }
            forecast_data.append(weather_info)
        
        return forecast_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast weather data: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return []

def get_historical_weather(api_key, city, days=5, units="metric"):
    """
    Get historical weather data for a specific city for the past N days.
    Note: This requires a paid OpenWeatherMap subscription.
    
    Parameters:
    - api_key: OpenWeatherMap API key
    - city: City name (e.g., "London,UK")
    - days: Number of past days to fetch data for
    - units: Units of measurement ("metric", "imperial", or "standard")
    
    Returns:
    - List of dictionaries containing weather data or empty list if request fails
    """
    # First get lat/lon coordinates for the city
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    
    try:
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        
        geo_data = geo_response.json()
        if not geo_data:
            print(f"Could not find coordinates for city: {city}")
            return []
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        
        # Collect historical data for each of the past N days
        historical_data = []
        today = datetime.now()
        
        for day_offset in range(1, days + 1):
            # Calculate the date for this historical data point
            past_date = today - timedelta(days=day_offset)
            # Convert to Unix timestamp
            past_timestamp = int(past_date.timestamp())
            
            # OpenWeatherMap One Call API 3.0 for historical data
            hist_url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={past_timestamp}&units={units}&appid={api_key}"
            
            hist_response = requests.get(hist_url)
            hist_response.raise_for_status()
            
            hist_data = hist_response.json()
            
            # Check if historical data was returned
            if 'data' in hist_data:
                for item in hist_data['data']:
                    weather_info = {
                        'date_time': datetime.fromtimestamp(item['dt']),
                        'temperature': item['temp'],
                        'humidity': item['humidity'],
                        'wind_speed': item['wind_speed'],
                        'weather_condition': item['weather'][0]['main'],
                        'weather_description': item['weather'][0]['description'],
                        'city': city,
                        'data_type': 'historical'
                    }
                    historical_data.append(weather_info)
            
            # Respect API rate limits
            time.sleep(1.1)
        
        return historical_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical weather data: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        print("Note: Historical data requires a paid OpenWeatherMap subscription.")
        return []

def generate_simulated_historical_data(current_data, days=5, hours_per_day=8):
    """
    Generate simulated historical weather data based on current conditions.
    This is used when actual historical API access is not available.
    
    Parameters:
    - current_data: Dictionary with current weather data
    - days: Number of past days to generate data for
    - hours_per_day: Number of data points per day
    
    Returns:
    - List of dictionaries containing simulated historical weather data
    """
    if not current_data:
        return []
    
    simulated_data = []
    now = datetime.now()
    
    # Common weather conditions for simulating transitions
    weather_conditions = ["Clear", "Clouds", "Rain", "Drizzle", "Thunderstorm", "Snow", "Mist", "Fog"]
    
    # Weather descriptions for each condition
    weather_descriptions = {
        "Clear": ["clear sky"],
        "Clouds": ["few clouds", "scattered clouds", "broken clouds", "overcast clouds"],
        "Rain": ["light rain", "moderate rain", "heavy rain", "very heavy rain"],
        "Drizzle": ["light intensity drizzle", "drizzle", "heavy intensity drizzle"],
        "Thunderstorm": ["thunderstorm with light rain", "thunderstorm", "heavy thunderstorm"],
        "Snow": ["light snow", "snow", "heavy snow"],
        "Mist": ["mist"],
        "Fog": ["fog"]
    }
    
    # Start with the current weather condition and temperature
    last_condition = current_data['weather_condition']
    base_temp = current_data['temperature']
    base_humidity = current_data['humidity']
    base_wind_speed = current_data['wind_speed']
    city = current_data['city']
    
    # Generate data for each day
    for day in range(1, days + 1):
        # Each day has a slight shift in base temperature (seasonal variation)
        day_temp_shift = random.uniform(-2.0, 2.0)
        
        for hour in range(hours_per_day):
            # Calculate timestamp for this data point
            past_time = now - timedelta(days=day, hours=(24 - hour * 24 // hours_per_day) % 24)
            
            # Determine if weather condition should change (20% chance)
            if random.random() < 0.2:
                # More likely to change to a similar condition
                weights = [0.3 if c == last_condition else 0.1 for c in weather_conditions]
                last_condition = random.choices(weather_conditions, weights=weights, k=1)[0]
            
            # Select a random description for this condition
            description = random.choice(weather_descriptions[last_condition])
            
            # Temperature varies by time of day (diurnal cycle) and random fluctuation
            hour_of_day = past_time.hour
            diurnal_effect = -3 + 6 * max(0, min(1, (hour_of_day - 5) / 12))  # Coldest at 5am, warmest at 5pm
            random_temp_fluctuation = random.uniform(-1.5, 1.5)
            temp = base_temp + day_temp_shift + diurnal_effect + random_temp_fluctuation
            
            # Humidity varies inversely with temperature plus random fluctuation
            humidity_fluctuation = random.uniform(-8, 8)
            humidity = max(10, min(100, base_humidity - (temp - base_temp) * 2 + humidity_fluctuation))
            
            # Wind speed varies randomly
            wind_fluctuation = random.uniform(-1, 1)
            wind_speed = max(0, base_wind_speed + wind_fluctuation)
            
            # Create data point
            weather_info = {
                'date_time': past_time,
                'temperature': round(temp, 1),
                'humidity': round(humidity),
                'wind_speed': round(wind_speed, 1),
                'weather_condition': last_condition,
                'weather_description': description,
                'city': city,
                'data_type': 'simulated_historical'
            }
            
            simulated_data.append(weather_info)
    
    return simulated_data

def collect_weather_data(api_key, cities=None, output_dir="data", historical=False, days=5, simulate_historical=True):
    """
    Collect current, forecast, and historical weather data for specified cities.
    
    Parameters:
    - api_key: OpenWeatherMap API key
    - cities: List of city names (default: ["London,UK", "New York,US", "Tokyo,JP"])
    - output_dir: Directory to save the CSV file
    - historical: Whether to try fetching historical data (requires paid API)
    - days: Number of past days to fetch/simulate historical data for
    - simulate_historical: Whether to generate simulated historical data
    
    Returns:
    - Path to the saved CSV file
    """
    if cities is None:
        cities = ["London,UK", "New York,US", "Tokyo,JP"]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Collect all weather data
    all_weather_data = []
    
    for city in cities:
        print(f"Collecting weather data for {city}...")
        
        # Get current weather
        current_data = get_current_weather(api_key, city)
        if current_data:
            all_weather_data.append(current_data)
            print(f"  Current temperature: {current_data['temperature']}°C")
        else:
            print(f"  Failed to get current weather for {city}")
            continue  # Skip to next city if we can't get current weather
        
        # Get forecast weather
        forecast_data = get_forecast_weather(api_key, city)
        if forecast_data:
            all_weather_data.extend(forecast_data)
            print(f"  Collected {len(forecast_data)} forecast data points")
        else:
            print(f"  Failed to get forecast data for {city}")
        
        # Try to get historical data if requested (and if user has paid API)
        if historical:
            print(f"  Attempting to collect historical data for past {days} days...")
            historical_data = get_historical_weather(api_key, city, days)
            if historical_data:
                all_weather_data.extend(historical_data)
                print(f"  Collected {len(historical_data)} historical data points")
            else:
                print(f"  Could not collect historical data (requires paid API access)")
                
                # Generate simulated historical data if requested and actual historical data not available
                if simulate_historical:
                    print(f"  Generating simulated historical data for past {days} days...")
                    simulated_data = generate_simulated_historical_data(current_data, days)
                    all_weather_data.extend(simulated_data)
                    print(f"  Generated {len(simulated_data)} simulated historical data points")
        
        # Generate simulated historical data if historical data was not requested but simulation is
        elif simulate_historical:
            print(f"  Generating simulated historical data for past {days} days...")
            simulated_data = generate_simulated_historical_data(current_data, days)
            all_weather_data.extend(simulated_data)
            print(f"  Generated {len(simulated_data)} simulated historical data points")
        
        # Respect API rate limits
        time.sleep(1)
    
    # Convert to DataFrame
    if all_weather_data:
        df = pd.DataFrame(all_weather_data)
        
        # Sort by city and date_time
        df = df.sort_values(['city', 'date_time'])
        
        # Format date_time as ISO format
        df['date_time'] = df['date_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"weather_data_{timestamp}.csv"
        file_path = os.path.join(output_dir, filename)
        
        # Save to CSV
        df.to_csv("../data/raw_data.csv", index=False)
        print(f"\nWeather data saved")
        
        # Display summary of the data
        print("\nData summary:")
        print(f"Total data points: {len(df)}")
        
        # Summary by city and data type
        summary = df.groupby(['city', 'data_type']).size().reset_index(name='count')
        print(summary)
        
        # Display sample of the data
        print("\nSample data:")
        print(df[['date_time', 'city', 'temperature', 'humidity', 'wind_speed', 'weather_condition', 'data_type']].head())
        
        return file_path
    else:
        print("No weather data collected.")
        return None

def main():
    """Main function to parse arguments and collect weather data."""
    parser = argparse.ArgumentParser(description='Collect weather data from OpenWeatherMap API')
    parser.add_argument('--api-key', '-k', type=str, help='OpenWeatherMap API key')
    parser.add_argument('--cities', '-c', type=str, nargs='+', 
                        help='Cities to collect weather data for (e.g., "London,UK" "New York,US")')
    parser.add_argument('--output-dir', '-o', type=str, default='data',
                        help='Directory to save the weather data CSV file')
    parser.add_argument('--days', '-d', type=int, default=5,
                        help='Number of past days to collect/simulate historical data for (default: 5)')
    parser.add_argument('--historical', '-hist', action='store_true',
                        help='Attempt to fetch historical data (requires paid API access)')
    parser.add_argument('--no-simulate', '-ns', action='store_true',
                        help='Do not generate simulated historical data if actual data is unavailable')
    
    args = parser.parse_args()
    
    # Use API key from arguments, environment variable, or prompt user
    api_key = "b2c2355ed1dffe138450b84b0b19cdce"
    
    if not api_key:
        api_key = input("Please enter your OpenWeatherMap API key: ")
    
    collect_weather_data(
        api_key=api_key, 
        cities=args.cities, 
        output_dir=args.output_dir,
        historical=args.historical,
        days=args.days,
        simulate_historical=not args.no_simulate
    )

if __name__ == "__main__":
    main()