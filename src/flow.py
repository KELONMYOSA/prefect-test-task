from concurrent.futures import ThreadPoolExecutor

from prefect import flow, get_run_logger

from src.data import load_csv, process_row
from src.notification import send_telegram_message


@flow()
def data_pipeline(csv_file):
    logger = get_run_logger()
    logger.info("Starting data pipeline")

    df = load_csv(csv_file)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for _, row in df.iterrows():
            symbol = row["symbol"]
            futures.append(executor.submit(process_row, symbol))

    for future in futures:
        future.result()

    send_telegram_message("Data pipeline completed!")
    logger.info("Data pipeline completed!")
