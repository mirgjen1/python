import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"
df = pd.read_csv(file_path)

# Clean column names
df.columns = df.columns.str.strip()

# Convert Date column
df['Date'] = pd.to_datetime(df['Date'])

# Convert Price column to float
df['Price'] = df['Price'].str.replace(',', '').astype(float)

# Sort by date
df = df.sort_values('Date')

# Plot area chart
plt.figure()
plt.fill_between(df['Date'], df['Price'])

# Labels and title
plt.xlabel("Date")
plt.ylabel("BTC Price")
plt.title("Bitcoin Price Area Chart")

# Improve readability
plt.xticks(rotation=45)
plt.tight_layout()

# Show plot
plt.show()