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

# Calculate rolling standard deviation
window = 20
df['Rolling_STD'] = df['Price'].rolling(window).std()

# Plot
plt.figure()

plt.plot(df['Date'], df['Rolling_STD'], label='Rolling STD (20 days)')

# Labels
plt.title("Bitcoin Rolling Standard Deviation (Volatility)")
plt.xlabel("Date")
plt.ylabel("Standard Deviation")
plt.legend()

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()