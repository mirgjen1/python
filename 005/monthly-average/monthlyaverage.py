import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime
import calendar

# 🔹 Load the CSV
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"
df = pd.read_csv(file_path)

# 🔹 Clean column names
df.columns = df.columns.str.strip()

# 🔹 Based on your data format, rename columns properly
column_names = ['Date', 'Price', 'Open', 'High', 'Low', 'Volume', 'Change %']
if len(df.columns) == len(column_names):
    df.columns = column_names
else:
    # Try to map based on typical patterns
    for col in df.columns:
        col_lower = col.lower()
        if 'date' in col_lower:
            df.rename(columns={col: 'Date'}, inplace=True)
        elif 'price' in col_lower or 'close' in col_lower:
            df.rename(columns={col: 'Price'}, inplace=True)
        elif 'open' in col_lower:
            df.rename(columns={col: 'Open'}, inplace=True)
        elif 'high' in col_lower:
            df.rename(columns={col: 'High'}, inplace=True)
        elif 'low' in col_lower:
            df.rename(columns={col: 'Low'}, inplace=True)
        elif 'volume' in col_lower:
            df.rename(columns={col: 'Volume'}, inplace=True)
        elif 'change' in col_lower or '%' in col:
            df.rename(columns={col: 'Change %'}, inplace=True)

# 🔹 Clean numeric columns
numeric_cols = ['Price', 'Open', 'High', 'Low', 'Volume', 'Change %']
for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = df[col].str.replace('%', '', regex=False)
        df[col] = df[col].str.replace('K', '000', regex=False)
        df[col] = df[col].str.replace('M', '000000', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 🔹 Convert Date column and sort
if 'Date' in df.columns:
    try:
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    except:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.sort_values('Date').reset_index(drop=True)

# 🔹 Drop rows with NaN in essential columns
df = df.dropna(subset=['Date', 'Price'])

print(f"✅ Processed {len(df)} rows of data")
print(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")

# 🔹 Create monthly aggregation
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Month_Name'] = df['Date'].dt.strftime('%B')
df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')

# Calculate monthly averages
monthly_avg_price = df.groupby('Year_Month')['Price'].agg(['mean', 'median', 'min', 'max', 'std']).reset_index()
monthly_avg_price['Year'] = pd.to_datetime(monthly_avg_price['Year_Month']).dt.year
monthly_avg_price['Month'] = pd.to_datetime(monthly_avg_price['Year_Month']).dt.month
monthly_avg_price['Month_Name'] = pd.to_datetime(monthly_avg_price['Year_Month']).dt.strftime('%B')

# Monthly volume and returns if available
monthly_avg_volume = df.groupby('Year_Month')['Volume'].mean().reset_index() if 'Volume' in df.columns else None
monthly_avg_returns = df.groupby('Year_Month')['Change %'].mean().reset_index() if 'Change %' in df.columns else None

# 🔹 1. MONTHLY AVERAGE PRICE CHART
fig1, ax1 = plt.subplots(figsize=(14, 7))
ax1.plot(monthly_avg_price['Year_Month'], monthly_avg_price['mean'], 
         marker='o', linewidth=2, markersize=6, color='blue', label='Average Price')
ax1.fill_between(monthly_avg_price['Year_Month'], 
                 monthly_avg_price['min'], monthly_avg_price['max'], 
                 alpha=0.2, color='blue', label='Min-Max Range')

ax1.set_xlabel('Month', fontsize=12)
ax1.set_ylabel('Price (USD)', fontsize=12)
ax1.set_title('Bitcoin Monthly Average Price Trend', fontsize=16, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend()
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 🔹 2. MONTHLY PRICE WITH ERROR BARS (Mean ± Std)
fig2, ax2 = plt.subplots(figsize=(14, 7))
ax2.errorbar(monthly_avg_price['Year_Month'], monthly_avg_price['mean'], 
             yerr=monthly_avg_price['std'], fmt='o-', capsize=5, 
             color='green', ecolor='lightgreen', linewidth=2, markersize=6,
             label='Mean ± 1 Std Dev')
ax2.set_xlabel('Month', fontsize=12)
ax2.set_ylabel('Price (USD)', fontsize=12)
ax2.set_title('Bitcoin Monthly Average Price with Volatility', fontsize=16, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 🔹 3. MONTHLY AVERAGE PRICE BAR CHART
fig3, ax3 = plt.subplots(figsize=(14, 7))
bars = ax3.bar(monthly_avg_price['Year_Month'], monthly_avg_price['mean'], 
               alpha=0.7, color='steelblue', edgecolor='black')

# Color bars based on price change
for i, (idx, row) in enumerate(monthly_avg_price.iterrows()):
    if i > 0:
        if row['mean'] > monthly_avg_price.iloc[i-1]['mean']:
            bars[i].set_color('green')
        else:
            bars[i].set_color('red')

ax3.set_xlabel('Month', fontsize=12)
ax3.set_ylabel('Average Price (USD)', fontsize=12)
ax3.set_title('Bitcoin Monthly Average Price - Bar Chart', fontsize=16, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 🔹 4. SEASONAL PATTERNS (Average by Month of Year)
fig4, ax4 = plt.subplots(figsize=(12, 6))

monthly_pattern = df.groupby('Month')['Price'].agg(['mean', 'median', 'std']).reset_index()
monthly_pattern['Month_Name'] = monthly_pattern['Month'].apply(lambda x: calendar.month_abbr[x])

ax4.bar(monthly_pattern['Month_Name'], monthly_pattern['mean'], 
        yerr=monthly_pattern['std'], capsize=5, alpha=0.7, 
        color='coral', edgecolor='black', label='Mean ± Std')
ax4.plot(monthly_pattern['Month_Name'], monthly_pattern['median'], 
         'ro-', linewidth=2, markersize=8, label='Median')

ax4.set_xlabel('Month', fontsize=12)
ax4.set_ylabel('Average Price (USD)', fontsize=12)
ax4.set_title('Bitcoin Seasonal Pattern - Average Price by Month', fontsize=16, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')
ax4.legend()
plt.tight_layout()
plt.show()

# 🔹 5. MONTHLY RETURNS CHART (if Change % available)
if 'Change %' in df.columns and monthly_avg_returns is not None:
    fig5, ax5 = plt.subplots(figsize=(14, 6))
    
    colors = ['green' if x > 0 else 'red' for x in monthly_avg_returns['Change %']]
    bars = ax5.bar(monthly_avg_returns['Year_Month'], monthly_avg_returns['Change %'], 
                   color=colors, alpha=0.7, edgecolor='black')
    
    ax5.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax5.set_xlabel('Month', fontsize=12)
    ax5.set_ylabel('Average Monthly Return (%)', fontsize=12)
    ax5.set_title('Bitcoin Monthly Average Returns', fontsize=16, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, val in zip(bars, monthly_avg_returns['Change %']):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height > 0 else -0.8),
                f'{val:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)
    
    plt.tight_layout()
    plt.show()

# 🔹 6. SUBPLOT: Price, Volume, and Returns together
if monthly_avg_volume is not None:
    fig6, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # Price subplot
    axes[0].plot(monthly_avg_price['Year_Month'], monthly_avg_price['mean'], 
                'b-o', linewidth=2, markersize=4)
    axes[0].set_ylabel('Avg Price (USD)', fontsize=11)
    axes[0].set_title('Bitcoin Monthly Averages', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Volume subplot
    axes[1].bar(monthly_avg_volume['Year_Month'], monthly_avg_volume['Volume'], 
               alpha=0.7, color='orange', edgecolor='black')
    axes[1].set_ylabel('Avg Volume', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    # Returns subplot
    if 'Change %' in df.columns:
        colors = ['green' if x > 0 else 'red' for x in monthly_avg_returns['Change %']]
        axes[2].bar(monthly_avg_returns['Year_Month'], monthly_avg_returns['Change %'], 
                   color=colors, alpha=0.7, edgecolor='black')
        axes[2].axhline(y=0, color='black', linestyle='-', linewidth=1)
        axes[2].set_ylabel('Avg Return (%)', fontsize=11)
        axes[2].grid(True, alpha=0.3)
    
    for ax in axes:
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()

# 🔹 7. HEATMAP: Monthly Price by Year
fig7, ax7 = plt.subplots(figsize=(12, 8))

# Create pivot table for heatmap
price_pivot = df.pivot_table(values='Price', index='Year', columns='Month', aggfunc='mean')
price_pivot.columns = [calendar.month_abbr[m] for m in price_pivot.columns]

# Create heatmap
im = ax7.imshow(price_pivot.values, cmap='YlOrRd', aspect='auto', interpolation='nearest')
ax7.set_xticks(range(len(price_pivot.columns)))
ax7.set_xticklabels(price_pivot.columns)
ax7.set_yticks(range(len(price_pivot.index)))
ax7.set_yticklabels(price_pivot.index)
ax7.set_xlabel('Month', fontsize=12)
ax7.set_ylabel('Year', fontsize=12)
ax7.set_title('Bitcoin Price Heatmap by Month and Year', fontsize=16, fontweight='bold')

# Add colorbar
plt.colorbar(im, ax=ax7, label='Average Price (USD)')

# Add text annotations
for i in range(len(price_pivot.index)):
    for j in range(len(price_pivot.columns)):
        text = ax7.text(j, i, f'{price_pivot.values[i, j]:.0f}',
                       ha="center", va="center", color="black", fontsize=8)

plt.tight_layout()
plt.show()

# 🔹 8. MONTHLY VOLATILITY CHART
fig8, ax8 = plt.subplots(figsize=(14, 6))

monthly_volatility = df.groupby('Year_Month')['Price'].std().reset_index()
monthly_volatility.columns = ['Year_Month', 'Volatility']

ax8.bar(monthly_volatility['Year_Month'], monthly_volatility['Volatility'], 
        alpha=0.7, color='purple', edgecolor='black')
ax8.set_xlabel('Month', fontsize=12)
ax8.set_ylabel('Price Volatility (Std Dev)', fontsize=12)
ax8.set_title('Bitcoin Monthly Price Volatility', fontsize=16, fontweight='bold')
ax8.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 🔹 9. BOX PLOT BY MONTH
fig9, ax9 = plt.subplots(figsize=(14, 7))

# Prepare data for boxplot
monthly_data = [df[df['Month'] == m]['Price'].values for m in range(1, 13)]
month_labels = [calendar.month_abbr[m] for m in range(1, 13)]

bp = ax9.boxplot(monthly_data, labels=month_labels, patch_artist=True)
for box in bp['boxes']:
    box.set(facecolor='lightblue', alpha=0.7)

ax9.set_xlabel('Month', fontsize=12)
ax9.set_ylabel('Price (USD)', fontsize=12)
ax9.set_title('Bitcoin Price Distribution by Month', fontsize=16, fontweight='bold')
ax9.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.show()

# 🔹 10. CUMULATIVE MONTHLY RETURNS
if 'Change %' in df.columns:
    fig10, ax10 = plt.subplots(figsize=(14, 6))
    
    cumulative_returns = (1 + df.groupby('Year_Month')['Change %'].mean() / 100).cumprod() - 1
    cumulative_returns = cumulative_returns * 100
    
    ax10.plot(cumulative_returns.index, cumulative_returns.values, 
             'g-o', linewidth=2, markersize=4)
    ax10.fill_between(cumulative_returns.index, 0, cumulative_returns.values, 
                      alpha=0.3, color='green')
    ax10.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax10.set_xlabel('Month', fontsize=12)
    ax10.set_ylabel('Cumulative Return (%)', fontsize=12)
    ax10.set_title('Bitcoin Cumulative Monthly Returns', fontsize=16, fontweight='bold')
    ax10.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# 🔹 PRINT STATISTICAL SUMMARY
print("\n" + "="*80)
print("MONTHLY AVERAGE ANALYSIS - STATISTICAL SUMMARY")
print("="*80)

print("\n📊 TOP 5 MONTHS WITH HIGHEST AVERAGE PRICE:")
top_months = monthly_avg_price.nlargest(5, 'mean')[['Year_Month', 'mean', 'median', 'std']]
for _, row in top_months.iterrows():
    print(f"  {row['Year_Month']}: ${row['mean']:,.2f} (Median: ${row['median']:,.2f}, Std: ${row['std']:,.2f})")

print("\n📉 TOP 5 MONTHS WITH LOWEST AVERAGE PRICE:")
bottom_months = monthly_avg_price.nsmallest(5, 'mean')[['Year_Month', 'mean', 'median', 'std']]
for _, row in bottom_months.iterrows():
    print(f"  {row['Year_Month']}: ${row['mean']:,.2f} (Median: ${row['median']:,.2f}, Std: ${row['std']:,.2f})")

print("\n📈 SEASONAL PATTERNS (Average Price by Month):")
for _, row in monthly_pattern.iterrows():
    print(f"  {row['Month_Name']}: ${row['mean']:,.2f} (Median: ${row['median']:,.2f})")

if 'Change %' in df.columns:
    print("\n💰 BEST MONTHS FOR RETURNS:")
    best_returns = monthly_avg_returns.nlargest(5, 'Change %')
    for _, row in best_returns.iterrows():
        print(f"  {row['Year_Month']}: {row['Change %']:.2f}%")
    
    print("\n💸 WORST MONTHS FOR RETURNS:")
    worst_returns = monthly_avg_returns.nsmallest(5, 'Change %')
    for _, row in worst_returns.iterrows():
        print(f"  {row['Year_Month']}: {row['Change %']:.2f}%")

print("\n📊 MONTHLY VOLATILITY STATISTICS:")
print(f"  Most volatile month: {monthly_volatility.loc[monthly_volatility['Volatility'].idxmax(), 'Year_Month']} "
      f"(${monthly_volatility['Volatility'].max():,.2f})")
print(f"  Least volatile month: {monthly_volatility.loc[monthly_volatility['Volatility'].idxmin(), 'Year_Month']} "
      f"(${monthly_volatility['Volatility'].min():,.2f})")

print("\n" + "="*80)
print("✅ Monthly average analysis complete!")