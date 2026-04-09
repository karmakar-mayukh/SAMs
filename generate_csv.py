import csv
import random
from datetime import datetime, timedelta


def generate_custom_csv(filename, num_rows=100):
    """
    Generates a custom CSV file with sample stock data.

    :param filename: Name of the CSV file to create
    :param num_rows: Number of rows to generate (default 100)
    """
    # CSV headers
    headers = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]

    # Start date
    start_date = datetime(2020, 1, 1)

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        current_price = 100.0  # Starting price

        for i in range(num_rows):
            # Generate date
            date = start_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            # Generate OHLC with some randomness
            open_price = current_price + random.uniform(-2, 2)
            high_price = open_price + random.uniform(0, 5)
            low_price = open_price - random.uniform(0, 5)
            close_price = random.uniform(low_price, high_price)

            # Adjust close for next day
            current_price = close_price

            # Adj Close same as Close for simplicity
            adj_close = close_price

            # Volume
            volume = random.randint(100000, 1000000)

            # Write row
            writer.writerow(
                [
                    date_str,
                    round(open_price, 2),
                    round(high_price, 2),
                    round(low_price, 2),
                    round(close_price, 2),
                    round(adj_close, 2),
                    volume,
                ]
            )


if __name__ == "__main__":
    generate_custom_csv("custom_stock_data.csv", 200)
    print("Custom CSV generated: custom_stock_data.csv")
