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

# Calculate daily returns (%)
df['Daily Return'] = df['Price'].pct_change() * 100

# Plot
plt.figure()

plt.plot(df['Date'], df['Daily Return'])

# Add zero line
plt.axhline(0)

# Labels
plt.title("Bitcoin Daily Returns (%)")
plt.xlabel("Date")
plt.ylabel("Daily Return (%)")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()