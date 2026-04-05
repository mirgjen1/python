import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"
df = pd.read_csv(file_path)

# Clean column names
df.columns = df.columns.str.strip()

# Convert Date
df['Date'] = pd.to_datetime(df['Date'])

# Convert Price
df['Price'] = df['Price'].str.replace(',', '').astype(float)

# Sort by date
df = df.sort_values('Date')

# Calculate Bollinger Bands
window = 20
df['MA20'] = df['Price'].rolling(window).mean()
df['STD'] = df['Price'].rolling(window).std()

df['Upper'] = df['MA20'] + (2 * df['STD'])
df['Lower'] = df['MA20'] - (2 * df['STD'])

# Plot
plt.figure()

plt.plot(df['Date'], df['Price'], label='Price')
plt.plot(df['Date'], df['MA20'], label='MA 20')
plt.plot(df['Date'], df['Upper'], label='Upper Band')
plt.plot(df['Date'], df['Lower'], label='Lower Band')

# Fill between bands
plt.fill_between(df['Date'], df['Lower'], df['Upper'], alpha=0.2)

# Labels
plt.title("Bitcoin Bollinger Bands")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()