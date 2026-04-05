import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime
import matplotlib.dates as mdates

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
df = df.dropna(subset=['Date'])

# Check if Volume column exists
if 'Volume' not in df.columns:
    print("❌ Volume column not found in the data!")
    print(f"Available columns: {df.columns.tolist()}")
    exit()

print(f"✅ Processed {len(df)} rows of data")
print(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"📊 Volume range: {df['Volume'].min():,.0f} to {df['Volume'].max():,.0f}")

# Extract date components for aggregation
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['Month_Name'] = df['Date'].dt.strftime('%B')
df['DayOfWeek'] = df['Date'].dt.dayofweek
df['DayName'] = df['Date'].dt.day_name()

# Convert volume to millions for better visualization
df['Volume_M'] = df['Volume'] / 1_000_000

# 🔹 1. BASIC VOLUME BAR CHART (Time Series)
fig1, ax1 = plt.subplots(figsize=(16, 6))

# Create bar chart
bars = ax1.bar(df['Date'], df['Volume_M'], width=0.8, color='steelblue', alpha=0.7, edgecolor='black')

# Color bars based on price change if available
if 'Change %' in df.columns:
    for i, (idx, row) in enumerate(df.iterrows()):
        if row['Change %'] > 0:
            bars[i].set_color('green')
            bars[i].set_alpha(0.7)
        elif row['Change %'] < 0:
            bars[i].set_color('red')
            bars[i].set_alpha(0.7)

ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Volume (Millions)', fontsize=12)
ax1.set_title('Bitcoin Daily Trading Volume', fontsize=16, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 🔹 2. VOLUME BAR CHART WITH PRICE OVERLAY
fig2, ax2 = plt.subplots(figsize=(16, 7))

# Create twin axis
ax2_twin = ax2.twinx()

# Plot volume bars
bars = ax2.bar(df['Date'], df['Volume_M'], width=0.8, color='lightblue', alpha=0.5, edgecolor='gray', label='Volume')

# Plot price line
ax2_twin.plot(df['Date'], df['Price'], color='red', linewidth=2, marker='o', markersize=3, label='Price')

# Color volume bars based on price movement
if 'Change %' in df.columns:
    for i, (idx, row) in enumerate(df.iterrows()):
        if i > 0:
            if row['Price'] > df.iloc[i-1]['Price']:
                bars[i].set_color('green')
                bars[i].set_alpha(0.6)
            else:
                bars[i].set_color('red')
                bars[i].set_alpha(0.6)

ax2.set_xlabel('Date', fontsize=12)
ax2.set_ylabel('Volume (Millions)', fontsize=12, color='blue')
ax2_twin.set_ylabel('Price (USD)', fontsize=12, color='red')
ax2.set_title('Bitcoin Volume and Price Relationship', fontsize=16, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')

# Add legend
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.tight_layout()
plt.show()

# 🔹 3. MONTHLY VOLUME BAR CHART
fig3, ax3 = plt.subplots(figsize=(14, 7))

# Aggregate volume by month
monthly_volume = df.groupby(df['Date'].dt.to_period('M')).agg({
    'Volume': 'sum',
    'Price': 'mean'
}).reset_index()
monthly_volume['Date'] = monthly_volume['Date'].dt.to_timestamp()
monthly_volume['Volume_M'] = monthly_volume['Volume'] / 1_000_000

# Create bar chart
bars = ax3.bar(monthly_volume['Date'], monthly_volume['Volume_M'], 
               width=20, color='teal', alpha=0.7, edgecolor='black')

# Add trend line
z = np.polyfit(range(len(monthly_volume)), monthly_volume['Volume_M'], 1)
p = np.poly1d(z)
ax3.plot(monthly_volume['Date'], p(range(len(monthly_volume))), 
         "r--", linewidth=2, alpha=0.8, label='Trend Line')

ax3.set_xlabel('Month', fontsize=12)
ax3.set_ylabel('Total Volume (Millions)', fontsize=12)
ax3.set_title('Bitcoin Monthly Total Trading Volume', fontsize=16, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45, ha='right')
ax3.legend()
plt.tight_layout()
plt.show()

# 🔹 4. VOLUME BY DAY OF WEEK
fig4, ax4 = plt.subplots(figsize=(12, 6))

# Aggregate volume by day of week
dow_volume = df.groupby('DayOfWeek').agg({
    'Volume': ['mean', 'median', 'std', 'count']
}).round(0)
dow_volume.columns = ['Mean', 'Median', 'Std', 'Count']
dow_volume['DayName'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_volume = dow_volume.set_index('DayName')
dow_volume['Volume_M'] = dow_volume['Mean'] / 1_000_000

# Reorder days
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_volume = dow_volume.reindex(days_order)

# Create bar chart with error bars
bars = ax4.bar(dow_volume.index, dow_volume['Volume_M'], 
               yerr=dow_volume['Std'] / 1_000_000, capsize=5,
               color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'],
               alpha=0.7, edgecolor='black')

# Add value labels
for bar, val in zip(bars, dow_volume['Volume_M']):
    ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
             f'{val:.1f}M', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax4.set_xlabel('Day of Week', fontsize=12)
ax4.set_ylabel('Average Daily Volume (Millions)', fontsize=12)
ax4.set_title('Bitcoin Average Trading Volume by Day of Week', fontsize=16, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 🔹 5. TOP VOLUME DAYS
fig5, ax5 = plt.subplots(figsize=(14, 8))

# Get top 20 volume days
top_volume_days = df.nlargest(20, 'Volume')[['Date', 'Volume_M', 'Price', 'Change %']].copy()
top_volume_days = top_volume_days.sort_values('Volume_M', ascending=True)

# Create horizontal bar chart
bars = ax5.barh(range(len(top_volume_days)), top_volume_days['Volume_M'], 
                color='coral', alpha=0.7, edgecolor='black')

# Color bars based on price change
if 'Change %' in top_volume_days.columns:
    for i, (idx, row) in enumerate(top_volume_days.iterrows()):
        if row['Change %'] > 0:
            bars[i].set_color('green')
        else:
            bars[i].set_color('red')

# Add labels
ax5.set_yticks(range(len(top_volume_days)))
ax5.set_yticklabels([d.strftime('%Y-%m-%d') for d in top_volume_days['Date']])
ax5.set_xlabel('Volume (Millions)', fontsize=12)
ax5.set_title('Top 20 Highest Volume Trading Days', fontsize=16, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='x')

# Add value labels
for i, (idx, row) in enumerate(top_volume_days.iterrows()):
    ax5.text(row['Volume_M'] + 0.5, i, f"{row['Volume_M']:.1f}M\n{row['Change %']:.1f}%",
             va='center', fontsize=9)

plt.tight_layout()
plt.show()

# 🔹 6. VOLUME DISTRIBUTION HISTOGRAM
fig6, (ax6a, ax6b) = plt.subplots(1, 2, figsize=(14, 5))

# Histogram
ax6a.hist(df['Volume_M'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
ax6a.axvline(df['Volume_M'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df["Volume_M"].mean():.1f}M')
ax6a.axvline(df['Volume_M'].median(), color='green', linestyle='--', linewidth=2, label=f'Median: {df["Volume_M"].median():.1f}M')
ax6a.set_xlabel('Volume (Millions)', fontsize=12)
ax6a.set_ylabel('Frequency', fontsize=12)
ax6a.set_title('Volume Distribution', fontsize=14, fontweight='bold')
ax6a.legend()
ax6a.grid(True, alpha=0.3)

# Box plot
box_data = [df[df['Year'] == year]['Volume_M'].values for year in sorted(df['Year'].unique())]
bp = ax6b.boxplot(box_data, labels=sorted(df['Year'].unique()), patch_artist=True)
for box in bp['boxes']:
    box.set(facecolor='lightblue', alpha=0.7)
ax6b.set_xlabel('Year', fontsize=12)
ax6b.set_ylabel('Volume (Millions)', fontsize=12)
ax6b.set_title('Volume Distribution by Year', fontsize=14, fontweight='bold')
ax6b.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# 🔹 7. VOLUME vs RETURNS SCATTER (Bubble Chart)
if 'Change %' in df.columns:
    fig7, ax7 = plt.subplots(figsize=(12, 8))
    
    # Create bubble chart
    scatter = ax7.scatter(df['Volume_M'], df['Change %'], 
                         s=df['Volume_M']/10, alpha=0.5, c=df['Change %'], 
                         cmap='RdYlGn', edgecolors='black', linewidth=0.5)
    
    ax7.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax7.set_xlabel('Volume (Millions)', fontsize=12)
    ax7.set_ylabel('Daily Return (%)', fontsize=12)
    ax7.set_title('Volume vs Returns Relationship', fontsize=16, fontweight='bold')
    ax7.grid(True, alpha=0.3)
    
    plt.colorbar(scatter, ax=ax7, label='Return (%)')
    plt.tight_layout()
    plt.show()

# 🔹 8. STACKED VOLUME BY MONTH (Year-over-Year Comparison)
fig8, ax8 = plt.subplots(figsize=(14, 8))

# Create pivot table for monthly volume by year
monthly_volume_pivot = df.pivot_table(values='Volume', 
                                     index='Year', 
                                     columns='Month', 
                                     aggfunc='sum', 
                                     fill_value=0) / 1_000_000

# Create stacked bar chart
monthly_volume_pivot.T.plot(kind='bar', stacked=True, ax=ax8, width=0.8, alpha=0.8)

ax8.set_xlabel('Month', fontsize=12)
ax8.set_ylabel('Total Volume (Millions)', fontsize=12)
ax8.set_title('Monthly Volume Comparison Across Years (Stacked)', fontsize=16, fontweight='bold')
ax8.set_xticklabels([calendar.month_abbr[i] for i in range(1, 13)], rotation=45)
ax8.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')
ax8.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.show()

# 🔹 9. VOLUME HEATMAP BY MONTH AND YEAR
fig9, ax9 = plt.subplots(figsize=(14, 8))

# Create pivot table for volume heatmap
volume_heatmap = df.pivot_table(values='Volume_M', 
                               index='Year', 
                               columns='Month', 
                               aggfunc='mean', 
                               fill_value=0)

# Create heatmap
im = ax9.imshow(volume_heatmap.values, cmap='YlOrRd', aspect='auto', interpolation='nearest')

ax9.set_xticks(range(12))
ax9.set_xticklabels([calendar.month_abbr[i] for i in range(1, 13)])
ax9.set_yticks(range(len(volume_heatmap.index)))
ax9.set_yticklabels(volume_heatmap.index)
ax9.set_xlabel('Month', fontsize=12)
ax9.set_ylabel('Year', fontsize=12)
ax9.set_title('Bitcoin Average Daily Volume Heatmap', fontsize=16, fontweight='bold')

# Add value annotations
for i in range(len(volume_heatmap.index)):
    for j in range(12):
        value = volume_heatmap.values[i, j]
        if value > 0:
            ax9.text(j, i, f'{value:.1f}', ha='center', va='center', 
                    fontsize=9, color='black' if value < volume_heatmap.values.max()/2 else 'white')

plt.colorbar(im, ax=ax9, label='Average Daily Volume (Millions)')
plt.tight_layout()
plt.show()

# 🔹 10. CUMULATIVE VOLUME OVER TIME
fig10, ax10 = plt.subplots(figsize=(14, 6))

# Calculate cumulative volume
df['Cumulative_Volume'] = df['Volume'].cumsum() / 1_000_000

# Create area chart
ax10.fill_between(df['Date'], df['Cumulative_Volume'], alpha=0.3, color='blue')
ax10.plot(df['Date'], df['Cumulative_Volume'], color='darkblue', linewidth=2)

# Add price on secondary axis
ax10_twin = ax10.twinx()
ax10_twin.plot(df['Date'], df['Price'], color='red', linewidth=1.5, alpha=0.7, label='Price')

ax10.set_xlabel('Date', fontsize=12)
ax10.set_ylabel('Cumulative Volume (Millions)', fontsize=12, color='blue')
ax10_twin.set_ylabel('Price (USD)', fontsize=12, color='red')
ax10.set_title('Bitcoin Cumulative Trading Volume Over Time', fontsize=16, fontweight='bold')
ax10.grid(True, alpha=0.3)
ax10.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax10.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 🔹 PRINT STATISTICAL SUMMARY
print("\n" + "="*80)
print("VOLUME ANALYSIS - STATISTICAL SUMMARY")
print("="*80)

print(f"\n📊 BASIC VOLUME STATISTICS:")
print(f"  Total Volume: {df['Volume'].sum():,.0f}")
print(f"  Average Daily Volume: {df['Volume'].mean():,.0f} ({df['Volume_M'].mean():.1f}M)")
print(f"  Median Daily Volume: {df['Volume'].median():,.0f} ({df['Volume_M'].median():.1f}M)")
print(f"  Max Daily Volume: {df['Volume'].max():,.0f} ({df['Volume_M'].max():.1f}M)")
print(f"  Min Daily Volume: {df['Volume'].min():,.0f} ({df['Volume_M'].min():.1f}M)")
print(f"  Std Deviation: {df['Volume'].std():,.0f} ({df['Volume_M'].std():.1f}M)")

print(f"\n📈 VOLUME BY DAY OF WEEK:")
for day in days_order:
    vol = dow_volume.loc[day, 'Mean']
    vol_m = vol / 1_000_000
    print(f"  {day}: {vol:,.0f} ({vol_m:.1f}M)")

print(f"\n🔥 TOP 5 HIGHEST VOLUME DAYS:")
for idx, row in df.nlargest(5, 'Volume')[['Date', 'Volume_M', 'Price', 'Change %']].iterrows():
    print(f"  {row['Date'].strftime('%Y-%m-%d')}: {row['Volume_M']:.1f}M | Price: ${row['Price']:,.0f} | Change: {row['Change %']:.2f}%")

print(f"\n📅 VOLUME BY YEAR:")
for year in sorted(df['Year'].unique()):
    year_data = df[df['Year'] == year]
    total_vol = year_data['Volume'].sum() / 1_000_000
    avg_vol = year_data['Volume'].mean() / 1_000_000
    print(f"  {year}: Total: {total_vol:.1f}M | Avg Daily: {avg_vol:.1f}M | Days: {len(year_data)}")

print(f"\n📆 VOLUME BY MONTH (Seasonality):")
for month in range(1, 13):
    month_data = df[df['Month'] == month]
    avg_vol = month_data['Volume'].mean() / 1_000_000
    print(f"  {calendar.month_name[month]}: {avg_vol:.1f}M")

print(f"\n💡 KEY INSIGHTS:")
print(f"  • Highest volume day: {df.loc[df['Volume'].idxmax(), 'Date'].strftime('%Y-%m-%d')} "
      f"({df['Volume_M'].max():.1f}M)")
print(f"  • Lowest volume day: {df.loc[df['Volume'].idxmin(), 'Date'].strftime('%Y-%m-%d')} "
      f"({df['Volume_M'].min():.1f}M)")
print(f"  • Volume spikes often {'accompany' if df[df['Volume'] > df['Volume'].quantile(0.95)]['Change %'].mean() > 0 else 'precede'} price movements")
print(f"  • Weekend volume is {((dow_volume.loc['Saturday', 'Mean'] + dow_volume.loc['Sunday', 'Mean']) / 2 / df['Volume'].mean() * 100):.1f}% of weekday average")

print("\n" + "="*80)

# Optional: Export volume analysis
volume_analysis = pd.DataFrame({
    'Statistic': ['Total Volume', 'Average Daily', 'Median Daily', 'Max Daily', 'Min Daily', 'Std Deviation'],
    'Value': [df['Volume'].sum(), df['Volume'].mean(), df['Volume'].median(), 
              df['Volume'].max(), df['Volume'].min(), df['Volume'].std()]
})
# Uncomment to save
# volume_analysis.to_csv('Bitcoin_Volume_Analysis.csv', index=False)
# print("\n✅ Volume analysis saved to 'Bitcoin_Volume_Analysis.csv'")

print("\n✅ Volume bar chart analysis complete!")