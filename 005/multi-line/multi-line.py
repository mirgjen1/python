import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"
df = pd.read_csv(file_path)

# Clean column names
df.columns = df.columns.str.strip()

# Convert Date column
df['Date'] = pd.to_datetime(df['Date'])

# Convert numeric columns (remove commas)
for col in ['Price', 'Open', 'High', 'Low']:
    df[col] = df[col].str.replace(',', '').astype(float)

# Sort by date
df = df.sort_values('Date')

# Plot multiple lines
plt.figure()

plt.plot(df['Date'], df['Price'], label='Close (Price)')
plt.plot(df['Date'], df['Open'], label='Open')
plt.plot(df['Date'], df['High'], label='High')
plt.plot(df['Date'], df['Low'], label='Low')

# Labels and title
plt.xlabel("Date")
plt.ylabel("Price")
plt.title("Bitcoin OHLC Multi-Line Chart")

# Legend
plt.legend()

# Improve readability
plt.xticks(rotation=45)
plt.tight_layout()

# Show plot
plt.show()