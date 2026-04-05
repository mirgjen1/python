import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import calendar
from datetime import datetime, timedelta
import seaborn as sns
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

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

# Extract date components
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['DayOfWeek'] = df['Date'].dt.dayofweek
df['DayName'] = df['Date'].dt.day_name()
df['WeekOfYear'] = df['Date'].dt.isocalendar().week

print(f"✅ Processed {len(df)} rows of data")
print(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"📊 Years available: {sorted(df['Year'].unique())}")

# 🔹 1. YEARLY CALENDAR HEATMAP (Returns)
def create_calendar_heatmap(data, year, metric='Change %', title_suffix='Returns'):
    """Create a calendar heatmap for a specific year"""
    
    # Filter data for the year
    year_data = data[data['Year'] == year].copy()
    
    if len(year_data) == 0:
        print(f"No data for year {year}")
        return None
    
    # Create a calendar matrix
    cal = calendar.monthcalendar(year, 1)
    months = range(1, 13)
    
    # Prepare the figure
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Create a grid for the calendar
    month_positions = {}
    current_row = 0
    
    for month in months:
        month_cal = calendar.monthcalendar(year, month)
        num_weeks = len(month_cal)
        
        month_positions[month] = (current_row, num_weeks)
        
        for week_idx, week in enumerate(month_cal):
            for day_idx, day in enumerate(week):
                if day != 0:
                    # Get data for this date
                    date = pd.Timestamp(year=year, month=month, day=day)
                    date_data = year_data[year_data['Date'] == date]
                    
                    if len(date_data) > 0:
                        value = date_data[metric].iloc[0]
                        color = get_color(value, metric)
                    else:
                        value = np.nan
                        color = 'lightgray'
                    
                    # Draw rectangle
                    rect = Rectangle((day_idx, current_row + week_idx), 0.95, 0.95, 
                                   facecolor=color, edgecolor='white', linewidth=0.5)
                    ax.add_patch(rect)
                    
                    # Add day number
                    ax.text(day_idx + 0.5, current_row + week_idx + 0.5, str(day),
                           ha='center', va='center', fontsize=8, color='black' if value != np.nan else 'gray')
                    
                    # Add value if significant
                    if not np.isnan(value) and abs(value) > 1:
                        value_text = f'{value:.1f}' if metric == 'Change %' else f'{value/1000:.0f}k'
                        ax.text(day_idx + 0.5, current_row + week_idx + 0.2, value_text,
                               ha='center', va='center', fontsize=6, color='black', alpha=0.7)
        
        current_row += num_weeks + 0.5  # Add spacing between months
    
    # Set axis limits and labels
    ax.set_xlim(0, 7)
    ax.set_ylim(current_row, 0)
    ax.set_xticks(np.arange(7) + 0.5)
    ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    
    # Add month labels
    for month, (start_row, num_weeks) in month_positions.items():
        ax.text(-0.5, start_row + num_weeks/2, calendar.month_name[month],
               ha='right', va='center', fontsize=10, fontweight='bold', rotation=0)
    
    ax.set_xlim(-1, 7)
    ax.set_title(f'Bitcoin {title_suffix} Calendar Heatmap - {year}', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Add colorbar
    if metric == 'Change %':
        norm = plt.Normalize(-5, 5)
        sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
        cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.02, aspect=50)
        cbar.set_label('Daily Return (%)', fontsize=10)
    else:
        norm = plt.Normalize(df[metric].min(), df[metric].max())
        sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
        cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.02, aspect=50)
        cbar.set_label(metric, fontsize=10)
    
    ax.axis('off')
    plt.tight_layout()
    plt.show()
    
    return fig

def get_color(value, metric):
    """Get color based on value and metric"""
    if pd.isna(value):
        return 'lightgray'
    
    if metric == 'Change %':
        # Red for negative, green for positive
        if value <= -3:
            return '#8B0000'  # Dark red
        elif value <= -1:
            return '#FF0000'  # Red
        elif value <= -0.5:
            return '#FF6666'  # Light red
        elif value <= 0:
            return '#FFCCCC'  # Very light red
        elif value < 0.5:
            return '#CCFFCC'  # Very light green
        elif value < 1:
            return '#66FF66'  # Light green
        elif value < 3:
            return '#00CC00'  # Green
        else:
            return '#006400'  # Dark green
    else:
        # For other metrics, use continuous colormap
        return plt.cm.viridis((value - df[metric].min()) / (df[metric].max() - df[metric].min()))

# Create calendar heatmaps for each year
for year in df['Year'].unique():
    create_calendar_heatmap(df, year, 'Change %', 'Daily Returns')

# 🔹 2. MONTHLY CALENDAR HEATMAP (All years combined)
fig2, axes2 = plt.subplots(3, 4, figsize=(20, 15))
fig2.suptitle('Bitcoin Monthly Returns Heatmap by Year', fontsize=18, fontweight='bold')

# Create pivot table for month-year returns
returns_pivot = df.pivot_table(values='Change %', 
                               index='Year', 
                               columns='Month', 
                               aggfunc='mean', 
                               fill_value=np.nan)

# Create heatmap for each month
for month in range(1, 13):
    row = (month - 1) // 4
    col = (month - 1) % 4
    ax = axes2[row, col]
    
    month_data = returns_pivot[month].dropna()
    
    if len(month_data) > 0:
        years = month_data.index
        returns = month_data.values
        
        colors = ['green' if x > 0 else 'red' for x in returns]
        bars = ax.bar(range(len(years)), returns, color=colors, alpha=0.7, edgecolor='black')
        
        # Add value labels
        for bar, val in zip(bars, returns):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (0.1 if height > 0 else -0.3),
                   f'{val:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)
        
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_title(calendar.month_name[month], fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(years)))
        ax.set_xticklabels(years, rotation=45, fontsize=8)
        ax.set_ylabel('Avg Return (%)', fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
    else:
        ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(calendar.month_name[month], fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()

# 🔹 3. WEEKLY CALENDAR HEATMAP
fig3, ax3 = plt.subplots(figsize=(16, 10))

# Create pivot table for week of year vs year
weekly_returns = df.pivot_table(values='Change %', 
                               index='Year', 
                               columns='WeekOfYear', 
                               aggfunc='mean', 
                               fill_value=np.nan)

# Create heatmap
im = ax3.imshow(weekly_returns.values, cmap='RdYlGn', aspect='auto', 
                interpolation='nearest', vmin=-3, vmax=3)

ax3.set_xticks(range(0, 54, 5))
ax3.set_xticklabels(range(1, 54, 5))
ax3.set_yticks(range(len(weekly_returns.index)))
ax3.set_yticklabels(weekly_returns.index)
ax3.set_xlabel('Week of Year', fontsize=12)
ax3.set_ylabel('Year', fontsize=12)
ax3.set_title('Bitcoin Weekly Returns Heatmap', fontsize=16, fontweight='bold')

plt.colorbar(im, ax=ax3, label='Average Weekly Return (%)')
plt.tight_layout()
plt.show()

# 🔹 4. DAY OF MONTH HEATMAP
fig4, ax4 = plt.subplots(figsize=(14, 8))

# Create pivot table for day of month vs month
day_of_month_returns = df.pivot_table(values='Change %', 
                                     index='Month', 
                                     columns='Day', 
                                     aggfunc='mean', 
                                     fill_value=np.nan)

# Reorder months
day_of_month_returns = day_of_month_returns.reindex(range(1, 13))

# Create heatmap
im = ax4.imshow(day_of_month_returns.values, cmap='RdYlGn', aspect='auto', 
                interpolation='nearest', vmin=-2, vmax=2)

ax4.set_xticks(range(0, 32, 5))
ax4.set_xticklabels(range(1, 32, 5))
ax4.set_yticks(range(12))
ax4.set_yticklabels([calendar.month_name[i] for i in range(1, 13)])
ax4.set_xlabel('Day of Month', fontsize=12)
ax4.set_ylabel('Month', fontsize=12)
ax4.set_title('Bitcoin Returns by Day of Month', fontsize=16, fontweight='bold')

plt.colorbar(im, ax=ax4, label='Average Return (%)')
plt.tight_layout()
plt.show()

# 🔹 5. QUARTERLY CALENDAR VIEW
fig5, axes5 = plt.subplots(2, 2, figsize=(16, 12))
fig5.suptitle('Bitcoin Quarterly Performance Heatmaps', fontsize=16, fontweight='bold')

quarters = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)]
quarter_names = ['Q1 (Jan-Mar)', 'Q2 (Apr-Jun)', 'Q3 (Jul-Sep)', 'Q4 (Oct-Dec)']

for idx, (q_months, q_name) in enumerate(zip(quarters, quarter_names)):
    row = idx // 2
    col = idx % 2
    ax = axes5[row, col]
    
    # Filter data for quarter
    quarter_data = df[df['Month'].isin(q_months)]
    
    # Create pivot table
    quarter_pivot = quarter_data.pivot_table(values='Change %', 
                                            index='Year', 
                                            columns='Month', 
                                            aggfunc='mean', 
                                            fill_value=np.nan)
    
    # Reorder columns
    quarter_pivot = quarter_pivot[[m for m in q_months if m in quarter_pivot.columns]]
    
    if len(quarter_pivot) > 0:
        im = ax.imshow(quarter_pivot.values, cmap='RdYlGn', aspect='auto', 
                      interpolation='nearest', vmin=-3, vmax=3)
        
        ax.set_xticks(range(len(quarter_pivot.columns)))
        ax.set_xticklabels([calendar.month_abbr[m] for m in quarter_pivot.columns])
        ax.set_yticks(range(len(quarter_pivot.index)))
        ax.set_yticklabels(quarter_pivot.index)
        ax.set_title(q_name, fontsize=12, fontweight='bold')
        
        # Add value annotations
        for i in range(len(quarter_pivot.index)):
            for j in range(len(quarter_pivot.columns)):
                value = quarter_pivot.values[i, j]
                if not np.isnan(value):
                    ax.text(j, i, f'{value:.1f}%', ha='center', va='center', 
                           fontsize=8, color='black' if abs(value) < 1.5 else 'white')
        
        plt.colorbar(im, ax=ax, label='Return (%)')
    else:
        ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(q_name, fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()

# 🔹 6. YEARLY RETURNS CALENDAR (Bar chart style)
fig6, ax6 = plt.subplots(figsize=(14, 8))

# Calculate monthly returns for each year
monthly_returns_by_year = df.pivot_table(values='Change %', 
                                        index='Year', 
                                        columns='Month', 
                                        aggfunc='mean', 
                                        fill_value=0)

# Create heatmap with enhanced styling
im = ax6.imshow(monthly_returns_by_year.values, cmap='RdYlGn', aspect='auto', 
                interpolation='nearest', vmin=-3, vmax=3)

ax6.set_xticks(range(12))
ax6.set_xticklabels([calendar.month_abbr[i] for i in range(1, 13)])
ax6.set_yticks(range(len(monthly_returns_by_year.index)))
ax6.set_yticklabels(monthly_returns_by_year.index)
ax6.set_xlabel('Month', fontsize=12)
ax6.set_ylabel('Year', fontsize=12)
ax6.set_title('Bitcoin Monthly Returns Calendar Heatmap', fontsize=16, fontweight='bold')

# Add value annotations
for i in range(len(monthly_returns_by_year.index)):
    for j in range(12):
        value = monthly_returns_by_year.values[i, j]
        if value != 0:
            color = 'white' if abs(value) > 2 else 'black'
            ax6.text(j, i, f'{value:.1f}%', ha='center', va='center', 
                    fontsize=9, color=color, fontweight='bold')

plt.colorbar(im, ax=ax6, label='Average Monthly Return (%)')
plt.tight_layout()
plt.show()

# 🔹 7. VOLUME CALENDAR HEATMAP
if 'Volume' in df.columns:
    fig7, ax7 = plt.subplots(figsize=(16, 10))
    
    # Normalize volume for better visualization
    df['Volume_Normalized'] = (df['Volume'] - df['Volume'].min()) / (df['Volume'].max() - df['Volume'].min())
    
    # Create volume pivot table
    volume_pivot = df.pivot_table(values='Volume_Normalized', 
                                 index='Year', 
                                 columns='Month', 
                                 aggfunc='mean', 
                                 fill_value=0)
    
    im = ax7.imshow(volume_pivot.values, cmap='YlOrRd', aspect='auto', interpolation='nearest')
    
    ax7.set_xticks(range(12))
    ax7.set_xticklabels([calendar.month_abbr[i] for i in range(1, 13)])
    ax7.set_yticks(range(len(volume_pivot.index)))
    ax7.set_yticklabels(volume_pivot.index)
    ax7.set_xlabel('Month', fontsize=12)
    ax7.set_ylabel('Year', fontsize=12)
    ax7.set_title('Bitcoin Trading Volume Calendar Heatmap', fontsize=16, fontweight='bold')
    
    plt.colorbar(im, ax=ax7, label='Normalized Volume')
    plt.tight_layout()
    plt.show()

# 🔹 8. STATISTICAL SUMMARY
print("\n" + "="*80)
print("CALENDAR HEATMAP ANALYSIS - STATISTICAL SUMMARY")
print("="*80)

# Best and worst months historically
monthly_avg = df.groupby('Month')['Change %'].agg(['mean', 'median', 'std']).round(4)
monthly_avg.index = [calendar.month_name[i] for i in monthly_avg.index]

print("\n📅 BEST MONTHS FOR BITCOIN (Historical Average Returns):")
best_months = monthly_avg.nlargest(3, 'mean')
for month, row in best_months.iterrows():
    print(f"  {month}: {row['mean']:.3f}% (Median: {row['median']:.3f}%, Std: {row['std']:.3f}%)")

print("\n📅 WORST MONTHS FOR BITCOIN (Historical Average Returns):")
worst_months = monthly_avg.nsmallest(3, 'mean')
for month, row in worst_months.iterrows():
    print(f"  {month}: {row['mean']:.3f}% (Median: {row['median']:.3f}%, Std: {row['std']:.3f}%)")

# Best and worst days of month
day_avg = df.groupby('Day')['Change %'].agg(['mean', 'count']).round(4)
print("\n📆 BEST DAYS OF MONTH (Top 5):")
best_days = day_avg.nlargest(5, 'mean')
for day, row in best_days.iterrows():
    print(f"  Day {int(day)}: {row['mean']:.3f}% (Sample size: {int(row['count'])})")

print("\n📆 WORST DAYS OF MONTH (Bottom 5):")
worst_days = day_avg.nsmallest(5, 'mean')
for day, row in worst_days.iterrows():
    print(f"  Day {int(day)}: {row['mean']:.3f}% (Sample size: {int(row['count'])})")

# Yearly performance
yearly_avg = df.groupby('Year')['Change %'].agg(['mean', 'sum']).round(2)
print("\n📊 YEARLY PERFORMANCE:")
for year, row in yearly_avg.iterrows():
    total_return = row['sum']
    performance = "🚀 BULLISH" if total_return > 50 else "📈 POSITIVE" if total_return > 0 else "📉 BEARISH" if total_return > -50 else "⚠️ VERY BEARISH"
    print(f"  {year}: Avg Daily: {row['mean']:.2f}% | Total Year Return: {total_return:.1f}% | {performance}")

# Calendar anomalies
print("\n🎯 CALENDAR ANOMALIES DETECTED:")
print(f"  • January Effect: {'Positive' if monthly_avg.loc['January', 'mean'] > 0 else 'Negative'} "
      f"({monthly_avg.loc['January', 'mean']:.2f}%)")
print(f"  • Summer Effect (Jun-Aug): {df[df['Month'].isin([6,7,8])]['Change %'].mean():.2f}%")
print(f"  • December Effect: {monthly_avg.loc['December', 'mean']:.2f}%")

print("\n" + "="*80)

# Optional: Export calendar data
calendar_data = df.groupby(['Year', 'Month', 'Day']).agg({
    'Change %': 'mean',
    'Volume': 'mean' if 'Volume' in df.columns else None,
    'Price': 'mean'
}).reset_index()

# Uncomment to save
# calendar_data.to_csv('Bitcoin_Calendar_Heatmap_Data.csv', index=False)
# print("\n✅ Calendar data saved to 'Bitcoin_Calendar_Heatmap_Data.csv'")

print("\n✅ Calendar heatmap analysis complete!")