import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import calendar
from datetime import datetime

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

# 🔹 Calculate Change % if not available
if 'Change %' not in df.columns and 'Price' in df.columns:
    print("⚠️ 'Change %' column not found. Calculating from Price column...")
    df['Change %'] = df['Price'].pct_change() * 100

# 🔹 Extract day of week information
df['DayOfWeek'] = df['Date'].dt.dayofweek  # 0=Monday, 6=Sunday
df['DayName'] = df['Date'].dt.day_name()

print(f"✅ Processed {len(df)} rows of data")
print(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"📊 Days of week in data: {df['DayName'].unique().tolist()}")

# 🔹 Calculate statistics by day of week
dow_stats = df.groupby('DayOfWeek').agg({
    'Change %': ['mean', 'median', 'std', 'count', 'min', 'max']
}).round(4)

dow_stats.columns = ['Mean', 'Median', 'Std', 'Count', 'Min', 'Max']
dow_stats['DayName'] = [calendar.day_name[i] for i in range(7)]
dow_stats = dow_stats.set_index('DayName')

# Reorder days to start from Monday
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_stats = dow_stats.reindex(days_order)

# Calculate win rate (percentage of positive returns)
win_rate = df.groupby('DayOfWeek').apply(
    lambda x: (x['Change %'] > 0).sum() / len(x) * 100
).round(2)
win_rate.index = [calendar.day_name[i] for i in range(7)]
win_rate = win_rate.reindex(days_order)

dow_stats['Win_Rate'] = win_rate.values

print("\n📊 Day of Week Statistics:")
print(dow_stats)

# 🔹 1. BAR CHART: Average Returns by Day of Week
fig1, ax1 = plt.subplots(figsize=(12, 6))

colors = ['green' if x > 0 else 'red' for x in dow_stats['Mean']]
bars = ax1.bar(dow_stats.index, dow_stats['Mean'], color=colors, alpha=0.7, edgecolor='black')

# Add error bars (standard deviation)
ax1.errorbar(dow_stats.index, dow_stats['Mean'], yerr=dow_stats['Std'], 
             fmt='none', capsize=5, color='gray', alpha=0.5)

# Add value labels on bars
for bar, val in zip(bars, dow_stats['Mean']):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + (0.05 if height > 0 else -0.15),
             f'{val:.2f}%', ha='center', va='bottom' if height > 0 else 'top', 
             fontsize=10, fontweight='bold')

ax1.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax1.set_xlabel('Day of Week', fontsize=12)
ax1.set_ylabel('Average Return (%)', fontsize=12)
ax1.set_title('Bitcoin: Average Daily Returns by Day of Week', fontsize=16, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 🔹 2. BOX PLOT: Return Distribution by Day of Week
fig2, ax2 = plt.subplots(figsize=(12, 6))

# Prepare data for boxplot
dow_data = [df[df['DayName'] == day]['Change %'].values for day in days_order]

bp = ax2.boxplot(dow_data, labels=days_order, patch_artist=True, showmeans=True)

# Customize box colors
colors_box = ['#FF9999', '#FFB366', '#FFD700', '#99FF99', '#66B3FF', '#C266FF', '#FF66B3']
for box, color in zip(bp['boxes'], colors_box):
    box.set(facecolor=color, alpha=0.7)

# Customize mean and median
bp['medians'][0].set(color='red', linewidth=2)
bp['means'][0].set(marker='D', markerfacecolor='blue', markersize=6)

ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
ax2.set_xlabel('Day of Week', fontsize=12)
ax2.set_ylabel('Return (%)', fontsize=12)
ax2.set_title('Bitcoin: Return Distribution by Day of Week', fontsize=16, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 🔹 3. WIN RATE CHART
fig3, ax3 = plt.subplots(figsize=(12, 6))

colors_win = ['green' if x > 50 else 'orange' if x == 50 else 'red' for x in dow_stats['Win_Rate']]
bars = ax3.bar(dow_stats.index, dow_stats['Win_Rate'], color=colors_win, alpha=0.7, edgecolor='black')

# Add value labels
for bar, val in zip(bars, dow_stats['Win_Rate']):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax3.axhline(y=50, color='black', linestyle='--', linewidth=1, label='50% (Random)')
ax3.set_xlabel('Day of Week', fontsize=12)
ax3.set_ylabel('Win Rate (%)', fontsize=12)
ax3.set_title('Bitcoin: Probability of Positive Returns by Day of Week', fontsize=16, fontweight='bold')
ax3.set_ylim([0, 100])
ax3.grid(True, alpha=0.3, axis='y')
ax3.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 🔹 4. SUBPLOT: Mean, Median, and Win Rate
fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(14, 6))

# Mean and Median chart
x = np.arange(len(dow_stats.index))
width = 0.35

bars1 = ax4a.bar(x - width/2, dow_stats['Mean'], width, label='Mean', 
                 color='steelblue', alpha=0.7, edgecolor='black')
bars2 = ax4a.bar(x + width/2, dow_stats['Median'], width, label='Median', 
                 color='lightcoral', alpha=0.7, edgecolor='black')

ax4a.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax4a.set_xlabel('Day of Week', fontsize=11)
ax4a.set_ylabel('Return (%)', fontsize=11)
ax4a.set_title('Mean vs Median Returns by Day', fontsize=12, fontweight='bold')
ax4a.set_xticks(x)
ax4a.set_xticklabels(dow_stats.index, rotation=45)
ax4a.legend()
ax4a.grid(True, alpha=0.3, axis='y')

# Win Rate chart
colors_win2 = ['green' if x > 50 else 'orange' if x == 50 else 'red' for x in dow_stats['Win_Rate']]
bars3 = ax4b.bar(dow_stats.index, dow_stats['Win_Rate'], color=colors_win2, alpha=0.7, edgecolor='black')

for bar, val in zip(bars3, dow_stats['Win_Rate']):
    height = bar.get_height()
    ax4b.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{val:.1f}%', ha='center', va='bottom', fontsize=9)

ax4b.axhline(y=50, color='black', linestyle='--', linewidth=1)
ax4b.set_xlabel('Day of Week', fontsize=11)
ax4b.set_ylabel('Win Rate (%)', fontsize=11)
ax4b.set_title('Win Rate by Day', fontsize=12, fontweight='bold')
ax4b.set_ylim([0, 100])
ax4b.grid(True, alpha=0.3, axis='y')
plt.setp(ax4b.get_xticklabels(), rotation=45)

plt.suptitle('Bitcoin Day of Week Analysis', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

# 🔹 5. HEATMAP: Returns by Day and Hour (if time data available)
# Create a more detailed analysis by day of week and week of year
fig5, ax5 = plt.subplots(figsize=(14, 8))

# Create pivot table for day of week vs week of year
df['WeekOfYear'] = df['Date'].dt.isocalendar().week
df['Year'] = df['Date'].dt.year

# Pivot table for average returns
returns_pivot = df.pivot_table(values='Change %', 
                               index='DayName', 
                               columns='WeekOfYear', 
                               aggfunc='mean', 
                               fill_value=0)

# Reorder days
returns_pivot = returns_pivot.reindex(days_order)

# Create heatmap
im = ax5.imshow(returns_pivot.values, cmap='RdYlGn', aspect='auto', interpolation='nearest', vmin=-5, vmax=5)

ax5.set_xticks(range(0, len(returns_pivot.columns), 5))
ax5.set_xticklabels(returns_pivot.columns[::5])
ax5.set_yticks(range(len(returns_pivot.index)))
ax5.set_yticklabels(returns_pivot.index)
ax5.set_xlabel('Week of Year', fontsize=12)
ax5.set_ylabel('Day of Week', fontsize=12)
ax5.set_title('Bitcoin Returns Heatmap: Day of Week vs Week of Year', fontsize=14, fontweight='bold')

plt.colorbar(im, ax=ax5, label='Average Return (%)')
plt.tight_layout()
plt.show()

# 🔹 6. CUMULATIVE RETURNS BY DAY OF WEEK
fig6, ax6 = plt.subplots(figsize=(12, 6))

# Calculate cumulative returns for each day of week
cumulative_returns = {}
for day in days_order:
    day_data = df[df['DayName'] == day].copy()
    day_data = day_data.sort_values('Date')
    day_data['Cumulative_Return'] = (1 + day_data['Change %'] / 100).cumprod() - 1
    day_data['Cumulative_Return'] = day_data['Cumulative_Return'] * 100
    cumulative_returns[day] = day_data

# Plot cumulative returns
for day, color in zip(days_order, colors_box):
    data = cumulative_returns[day]
    ax6.plot(range(len(data)), data['Cumulative_Return'].values, 
            label=day, color=color, linewidth=2, alpha=0.7)

ax6.set_xlabel('Number of Trading Days (Chronological)', fontsize=12)
ax6.set_ylabel('Cumulative Return (%)', fontsize=12)
ax6.set_title('Bitcoin: Cumulative Returns by Day of Week', fontsize=16, fontweight='bold')
ax6.legend(loc='best', ncol=2)
ax6.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 🔹 7. RADAR/SPIDER CHART
fig7, ax7 = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

# Prepare data for radar chart
angles = np.linspace(0, 2 * np.pi, len(days_order), endpoint=False).tolist()
angles += angles[:1]  # Close the loop

# Normalize data for radar chart (0-1 scale)
mean_returns_norm = (dow_stats['Mean'] - dow_stats['Mean'].min()) / (dow_stats['Mean'].max() - dow_stats['Mean'].min())
win_rate_norm = dow_stats['Win_Rate'] / 100

# Plot multiple metrics
values_mean = mean_returns_norm.tolist()
values_mean += values_mean[:1]
values_win = win_rate_norm.tolist()
values_win += values_win[:1]

ax7.plot(angles, values_mean, 'o-', linewidth=2, label='Mean Returns (normalized)', color='blue')
ax7.fill(angles, values_mean, alpha=0.25, color='blue')
ax7.plot(angles, values_win, 'o-', linewidth=2, label='Win Rate', color='green')
ax7.fill(angles, values_win, alpha=0.25, color='green')

ax7.set_xticks(angles[:-1])
ax7.set_xticklabels(days_order)
ax7.set_ylim(0, 1)
ax7.set_title('Bitcoin: Day of Week Performance Radar Chart', fontsize=14, fontweight='bold', pad=20)
ax7.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
ax7.grid(True)
plt.tight_layout()
plt.show()

# 🔹 8. VIOLIN PLOT for detailed distribution
fig8, ax8 = plt.subplots(figsize=(14, 7))

# Create violin plot
parts = ax8.violinplot(dow_data, positions=range(len(days_order)), 
                       showmeans=True, showmedians=True, widths=0.7)

# Customize violin colors
for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(colors_box[i])
    pc.set_alpha(0.7)
    pc.set_edgecolor('black')

parts['cmeans'].set_color('blue')
parts['cmeans'].set_markersize(8)
parts['cmedians'].set_color('red')
parts['cmedians'].set_linewidth(2)

ax8.set_xticks(range(len(days_order)))
ax8.set_xticklabels(days_order, rotation=45)
ax8.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
ax8.set_xlabel('Day of Week', fontsize=12)
ax8.set_ylabel('Return (%)', fontsize=12)
ax8.set_title('Bitcoin: Return Distribution Violin Plot by Day of Week', fontsize=16, fontweight='bold')
ax8.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.show()

# 🔹 9. WEEKDAY vs WEEKEND COMPARISON
fig9, (ax9a, ax9b) = plt.subplots(1, 2, figsize=(12, 5))

# Classify days
df['DayType'] = df['DayName'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')

weekday_stats = df.groupby('DayType')['Change %'].agg(['mean', 'median', 'std', 'count'])

# Bar chart comparison
weekday_names = ['Weekday', 'Weekend']
weekday_means = [weekday_stats.loc['Weekday', 'mean'], weekday_stats.loc['Weekend', 'mean']]
weekday_errors = [weekday_stats.loc['Weekday', 'std'], weekday_stats.loc['Weekend', 'std']]

bars = ax9a.bar(weekday_names, weekday_means, yerr=weekday_errors, 
                capsize=5, color=['steelblue', 'orange'], alpha=0.7, edgecolor='black')
ax9a.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax9a.set_ylabel('Average Return (%)', fontsize=11)
ax9a.set_title('Weekday vs Weekend Returns', fontsize=12, fontweight='bold')
ax9a.grid(True, alpha=0.3, axis='y')

# Box plot comparison
weekday_data = [df[df['DayType'] == 'Weekday']['Change %'].values,
                df[df['DayType'] == 'Weekend']['Change %'].values]
bp2 = ax9b.boxplot(weekday_data, labels=weekday_names, patch_artist=True)
bp2['boxes'][0].set(facecolor='steelblue', alpha=0.7)
bp2['boxes'][1].set(facecolor='orange', alpha=0.7)
ax9b.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax9b.set_ylabel('Return (%)', fontsize=11)
ax9b.set_title('Return Distribution: Weekday vs Weekend', fontsize=12, fontweight='bold')
ax9b.grid(True, alpha=0.3, axis='y')

plt.suptitle('Bitcoin: Weekday vs Weekend Performance', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# 🔹 10. STATISTICAL SUMMARY with Statistical Tests
print("\n" + "="*80)
print("DAY OF WEEK RETURNS ANALYSIS - STATISTICAL SUMMARY")
print("="*80)

print("\n📊 AVERAGE RETURNS BY DAY OF WEEK:")
for day in days_order:
    mean_val = dow_stats.loc[day, 'Mean']
    median_val = dow_stats.loc[day, 'Median']
    std_val = dow_stats.loc[day, 'Std']
    win_rate_val = dow_stats.loc[day, 'Win_Rate']
    count_val = dow_stats.loc[day, 'Count']
    
    # Determine performance rating
    if mean_val > 0.2:
        rating = "⭐⭐⭐ (Strongly Positive)"
    elif mean_val > 0:
        rating = "⭐⭐ (Slightly Positive)"
    elif mean_val > -0.2:
        rating = "⭐ (Slightly Negative)"
    else:
        rating = "⚠️ (Strongly Negative)"
    
    print(f"\n  {day}:")
    print(f"    Mean: {mean_val:.3f}% | Median: {median_val:.3f}% | Std: {std_val:.3f}%")
    print(f"    Win Rate: {win_rate_val:.1f}% | Sample Size: {count_val}")
    print(f"    Rating: {rating}")

# Best and worst days
best_day = dow_stats['Mean'].idxmax()
worst_day = dow_stats['Mean'].idxmin()
best_win_rate = dow_stats['Win_Rate'].idxmax()
worst_win_rate = dow_stats['Win_Rate'].idxmin()

print("\n🏆 BEST PERFORMING DAYS:")
print(f"  • Highest Average Return: {best_day} ({dow_stats.loc[best_day, 'Mean']:.3f}%)")
print(f"  • Highest Win Rate: {best_win_rate} ({dow_stats.loc[best_win_rate, 'Win_Rate']:.1f}%)")

print("\n📉 WORST PERFORMING DAYS:")
print(f"  • Lowest Average Return: {worst_day} ({dow_stats.loc[worst_day, 'Mean']:.3f}%)")
print(f"  • Lowest Win Rate: {worst_win_rate} ({dow_stats.loc[worst_win_rate, 'Win_Rate']:.1f}%)")

# Weekday vs Weekend t-test
from scipy import stats as scipy_stats

weekday_returns = df[df['DayType'] == 'Weekday']['Change %'].dropna()
weekend_returns = df[df['DayType'] == 'Weekend']['Change %'].dropna()

if len(weekday_returns) > 0 and len(weekend_returns) > 0:
    t_stat, p_value = scipy_stats.ttest_ind(weekday_returns, weekend_returns)
    
    print("\n📈 WEEKDAY vs WEEKEND STATISTICAL TEST:")
    print(f"  Weekday Mean: {weekday_returns.mean():.3f}% (n={len(weekday_returns)})")
    print(f"  Weekend Mean: {weekend_returns.mean():.3f}% (n={len(weekend_returns)})")
    print(f"  T-statistic: {t_stat:.4f}")
    print(f"  P-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("  ✓ Statistically significant difference (p < 0.05)")
    else:
        print("  ✗ No statistically significant difference (p ≥ 0.05)")

# Calculate day-of-week effect strength
print("\n💡 KEY INSIGHTS:")
print(f"  • Best day to buy: {best_day if dow_stats.loc[best_day, 'Mean'] < 0 else worst_day} (historically lowest returns)")
print(f"  • Best day to sell: {best_day if dow_stats.loc[best_day, 'Mean'] > 0 else worst_day} (historically highest returns)")
print(f"  • Most consistent day: {dow_stats['Std'].idxmin()} (lowest volatility)")
print(f"  • Most volatile day: {dow_stats['Std'].idxmax()} (highest volatility)")

print("\n" + "="*80)

# Optional: Save day of week statistics to CSV
dow_stats.to_csv('Bitcoin_Day_of_Week_Analysis.csv')
print("\n✅ Day of week statistics saved to 'Bitcoin_Day_of_Week_Analysis.csv'")
print("\n✅ Day of week analysis complete!")