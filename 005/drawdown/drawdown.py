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

# Calculate rolling peak
df['Peak'] = df['Price'].cummax()

# Calculate drawdown (%)
df['Drawdown'] = (df['Price'] - df['Peak']) / df['Peak'] * 100

# Plot
plt.figure()

plt.plot(df['Date'], df['Drawdown'], label='Drawdown (%)')

# Fill area (nice effect)
plt.fill_between(df['Date'], df['Drawdown'], 0, alpha=0.3)

# Labels
plt.title("Bitcoin Drawdown")
plt.xlabel("Date")
plt.ylabel("Drawdown (%)")
plt.legend()

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()