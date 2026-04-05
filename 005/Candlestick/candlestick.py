import pandas as pd
import mplfinance as mpf

# Load dataset
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"
df = pd.read_csv(file_path)

# Clean column names
df.columns = df.columns.str.strip()

# Convert Date column
df['Date'] = pd.to_datetime(df['Date'])

# Remove commas and convert numeric columns
for col in ['Price', 'Open', 'High', 'Low']:
    df[col] = df[col].str.replace(',', '').astype(float)

# Set Date as index
df.set_index('Date', inplace=True)

# Sort by date
df.sort_index(inplace=True)

# Rename columns for mplfinance (IMPORTANT)
df.rename(columns={
    'Price': 'Close',
    'Open': 'Open',
    'High': 'High',
    'Low': 'Low'
}, inplace=True)

# Plot candlestick chart
mpf.plot(
    df,
    type='candle',
    style='charles',
    title='Bitcoin Candlestick Chart',
    ylabel='Price',
    volume=False
)