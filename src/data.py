import json
import os
import time

import pandas as pd
import requests
from prefect import get_run_logger, task

from src.config import settings


# Чтение данных из CSV
@task(retries=3, retry_delay_seconds=10)
def load_csv(file_path):
    logger = get_run_logger()
    df = pd.read_csv(file_path, sep=";")
    logger.info(f"Loaded {len(df)} rows from {file_path}")
    return df


# Запрос к API
@task(retries=3, retry_delay_seconds=10)
def fetch_data(symbol):
    logger = get_run_logger()
    url = f"{settings.API_URL}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={settings.API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:  # noqa: PLR2004
        raise ValueError("API request failed")

    data = response.json()

    if "Time Series (Daily)" not in data:
        raise KeyError(f"Key 'Time Series (Daily)' not found in response for {symbol}. Response: {data}")

    logger.info(f"Fetched data for {symbol}")
    return data


# Обработка данных
@task
def process_data(data, symbol):
    time_series = data.get("Time Series (Daily)", {})

    if not time_series:
        raise ValueError(f"No 'Time Series (Daily)' data available for {symbol}")

    df = pd.DataFrame(data["Time Series (Daily)"]).transpose()
    df.columns = [f"{symbol}_{col}" for col in df.columns]
    return df


# Сохранение результатов в JSON
@task
def save_to_json(data, symbol):
    data_dict = data.to_dict(orient="records")

    file_path = f"data/processed/{symbol}.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data_dict, f, indent=4)
    return file_path


# Обработка строки
@task
def process_row(symbol):
    data = fetch_data(symbol)
    processed_data = process_data(data, symbol)
    save_to_json(processed_data, symbol)
    time.sleep(30)
