import requests
import pandas as pd
import streamlit as st

API_URL = "http://127.0.0.1:8000/api/"

def fetch_data(endpoint):
    try:
        url = f"{API_URL}{endpoint}/"
        print(f"Fetching {url}...")
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Success: {len(response.json())} items")
            return pd.DataFrame(response.json())
        print(f"Failed with status: {response.status_code}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Exception: {e}")
        return pd.DataFrame()

print("Testing connection...")
df_sensors = fetch_data("capteurs")
print("Sensors columns:", df_sensors.columns)

if not df_sensors.empty:
    df_sensors['latitude'] = pd.to_numeric(df_sensors['latitude'], errors='coerce')
    df_sensors['longitude'] = pd.to_numeric(df_sensors['longitude'], errors='coerce')
    print("Coordinates processed.")

print("Done.")
