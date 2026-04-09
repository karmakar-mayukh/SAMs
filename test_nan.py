import pandas as pd
import numpy as np

# Create dummy df
data = {
    'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
    'Open': [1, 2, 3],
    'High': [1, 2, 3],
    'Low': [1, 2, 3],
    'Close': [1, 2, np.nan],
    'Volume': [100, 200, 300]
}
df = pd.DataFrame(data)

today_stock = df.iloc[-1:]
print("Before dropna:")
print(today_stock['Open'].to_string(index=False))

df = df.dropna()
print("After dropna:")
print(today_stock['Open'].to_string(index=False))
