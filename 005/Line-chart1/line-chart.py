import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"

try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit()
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Clean column names (remove spaces if needed)
df.columns = df.columns.str.strip()

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Remove commas and convert Price to float
# Handle potential missing or non-numeric values
df['Price'] = df['Price'].astype(str).str.replace(',', '', regex=False)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

# Remove rows with NaN values in Price or Date
df = df.dropna(subset=['Price', 'Date'])

# Sort by date (important for line chart)
df = df.sort_values('Date')

# Plot line chart
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Price'], linewidth=1.5, color='blue')

# Labels and title
plt.xlabel("Date", fontsize=12)
plt.ylabel("BTC Price (USD)", fontsize=12)
plt.title("Bitcoin Price Over Time", fontsize=14, fontweight='bold')

# Format y-axis to show large numbers nicely
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Rotate date labels for readability
plt.xticks(rotation=45, ha='right')

# Add grid for better readability
plt.grid(True, alpha=0.3, linestyle='--')

# Adjust layout and show plot
plt.tight_layout()
plt.show()

# Print some basic info about the data
print(f"Data range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Number of data points: {len(df)}")
print(f"Price range: ${df['Price'].min():,.2f} to ${df['Price'].max():,.2f}")