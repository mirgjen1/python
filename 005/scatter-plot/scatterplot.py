import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 🔹 Load the CSV
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"
df = pd.read_csv(file_path)

# 🔹 Clean column names
df.columns = df.columns.str.strip()

# 🔹 Check the actual columns from your data
print("Available columns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# 🔹 Based on your data format, let's rename columns properly
# Your data appears to have: Date, Price, Open, High, Low, Volume, Change%
column_names = ['Date', 'Price', 'Open', 'High', 'Low', 'Volume', 'Change %']
if len(df.columns) == len(column_names):
    df.columns = column_names
else:
    # Try to map based on typical patterns
    for i, col in enumerate(df.columns):
        if 'date' in col.lower():
            df.rename(columns={col: 'Date'}, inplace=True)
        elif 'price' in col.lower() or 'close' in col.lower():
            df.rename(columns={col: 'Price'}, inplace=True)
        elif 'open' in col.lower():
            df.rename(columns={col: 'Open'}, inplace=True)
        elif 'high' in col.lower():
            df.rename(columns={col: 'High'}, inplace=True)
        elif 'low' in col.lower():
            df.rename(columns={col: 'Low'}, inplace=True)
        elif 'volume' in col.lower():
            df.rename(columns={col: 'Volume'}, inplace=True)
        elif 'change' in col.lower() or '%' in col:
            df.rename(columns={col: 'Change %'}, inplace=True)

# 🔹 Clean numeric columns
numeric_cols = ['Price', 'Open', 'High', 'Low', 'Volume', 'Change %']
for col in numeric_cols:
    if col in df.columns:
        # Remove commas and convert to numeric
        df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = df[col].str.replace('%', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 🔹 Convert Date column
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df = df.sort_values('Date')  # Sort by date

# 🔹 Drop rows with NaN
df = df.dropna()

print(f"\nProcessed {len(df)} rows of data")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")

# 🔹 Create multiple scatter plots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Bitcoin Price Analysis - Scatter Plots', fontsize=16, fontweight='bold')

# 1. Price vs Volume (with color showing price)
scatter1 = axes[0, 0].scatter(df['Volume'], df['Price'], 
                              c=df['Price'], cmap='viridis', 
                              alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
axes[0, 0].set_xlabel('Volume', fontsize=12)
axes[0, 0].set_ylabel('Price (USD)', fontsize=12)
axes[0, 0].set_title('Price vs Volume', fontsize=12, fontweight='bold')
axes[0, 0].grid(True, alpha=0.3)
plt.colorbar(scatter1, ax=axes[0, 0], label='Price (USD)')

# 2. Date vs Price with color showing volume
scatter2 = axes[0, 1].scatter(df['Date'], df['Price'], 
                              c=df['Volume'], cmap='plasma', 
                              alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
axes[0, 1].set_xlabel('Date', fontsize=12)
axes[0, 1].set_ylabel('Price (USD)', fontsize=12)
axes[0, 1].set_title('Price Trend Over Time', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)
plt.colorbar(scatter2, ax=axes[0, 1], label='Volume')
axes[0, 1].tick_params(axis='x', rotation=45)

# 3. Volume vs Change % (returns)
scatter3 = axes[1, 0].scatter(df['Change %'], df['Volume'], 
                              c=df['Change %'], cmap='RdYlGn', 
                              alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
axes[1, 0].set_xlabel('Daily Return (%)', fontsize=12)
axes[1, 0].set_ylabel('Volume', fontsize=12)
axes[1, 0].set_title('Volume vs Daily Returns', fontsize=12, fontweight='bold')
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].axvline(x=0, color='black', linestyle='--', alpha=0.5)
plt.colorbar(scatter3, ax=axes[1, 0], label='Return (%)')

# 4. Price vs Change % (returns)
scatter4 = axes[1, 1].scatter(df['Price'], df['Change %'], 
                              c=df['Volume'], cmap='coolwarm', 
                              alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
axes[1, 1].set_xlabel('Price (USD)', fontsize=12)
axes[1, 1].set_ylabel('Daily Return (%)', fontsize=12)
axes[1, 1].set_title('Returns vs Price Level', fontsize=12, fontweight='bold')
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
plt.colorbar(scatter4, ax=axes[1, 1], label='Volume')

plt.tight_layout()
plt.show()

# 🔹 Additional detailed scatter plots
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6))
fig2.suptitle('Advanced Bitcoin Analysis', fontsize=14, fontweight='bold')

# High-Low spread vs Volume
df['Spread'] = df['High'] - df['Low']
scatter5 = axes2[0].scatter(df['Spread'], df['Volume'], 
                            c=df['Change %'], cmap='RdYlGn', 
                            alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
axes2[0].set_xlabel('Daily High-Low Spread (USD)', fontsize=12)
axes2[0].set_ylabel('Volume', fontsize=12)
axes2[0].set_title('Volatility vs Volume', fontsize=12, fontweight='bold')
axes2[0].grid(True, alpha=0.3)
plt.colorbar(scatter5, ax=axes2[0], label='Return (%)')

# Price vs Daily Range percentage
df['Range %'] = ((df['High'] - df['Low']) / df['Low']) * 100
scatter6 = axes2[1].scatter(df['Price'], df['Range %'], 
                            c=df['Volume'], cmap='viridis', 
                            alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
axes2[1].set_xlabel('Price (USD)', fontsize=12)
axes2[1].set_ylabel('Daily Range (%)', fontsize=12)
axes2[1].set_title('Volatility at Different Price Levels', fontsize=12, fontweight='bold')
axes2[1].grid(True, alpha=0.3)
plt.colorbar(scatter6, ax=axes2[1], label='Volume')

plt.tight_layout()
plt.show()

# 🔹 Print correlation matrix
print("\n" + "="*60)
print("CORRELATION MATRIX")
print("="*60)
numeric_df = df[['Price', 'Open', 'High', 'Low', 'Volume', 'Change %', 'Spread', 'Range %']]
correlation = numeric_df.corr()
print(correlation.round(4))
print("="*60)

# 🔹 Highlight key insights
print("\n🔍 KEY INSIGHTS:")
print("-"*40)
price_vol_corr = correlation.loc['Price', 'Volume']
print(f"• Price-Volume correlation: {price_vol_corr:.3f} {'(Positive)' if price_vol_corr > 0 else '(Negative)'}")

returns_vol_corr = correlation.loc['Change %', 'Volume']
print(f"• Returns-Volume correlation: {returns_vol_corr:.3f}")

volatility_vol_corr = correlation.loc['Range %', 'Volume']
print(f"• Volatility-Volume correlation: {volatility_vol_corr:.3f}")

# Find extreme days
max_return_day = df.loc[df['Change %'].idxmax()]
min_return_day = df.loc[df['Change %'].idxmin()]
print(f"\n• Best day: {max_return_day['Date'].date()} with +{max_return_day['Change %']:.2f}% return")
print(f"• Worst day: {min_return_day['Date'].date()} with {min_return_day['Change %']:.2f}% return")

highest_volume_day = df.loc[df['Volume'].idxmax()]
print(f"• Highest volume day: {highest_volume_day['Date'].date()} with {highest_volume_day['Volume']:,.0f} volume")