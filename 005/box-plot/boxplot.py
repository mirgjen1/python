import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 🔹 Load the CSV
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"
df = pd.read_csv(file_path)

# 🔹 Clean column names
df.columns = df.columns.str.strip()

# 🔹 Check if '% Change' column exists (try alternative names if needed)
if '% Change' not in df.columns:
    # Try common alternatives
    possible_names = ['Change %', 'Change', '%Change', 'Percent Change']
    found = False
    for name in possible_names:
        if name in df.columns:
            print(f"Found column '{name}', renaming to '% Change'")
            df.rename(columns={name: '% Change'}, inplace=True)
            found = True
            break
    if not found:
        print("Column '% Change' not found. Available columns:", df.columns.tolist())
        exit()

# 🔹 Convert '% Change' to numeric (handle various formats)
# Convert to string first, then remove % symbol and any whitespace
df['% Change'] = df['% Change'].astype(str).str.strip()
df['% Change'] = df['% Change'].str.replace('%', '', regex=False)
df['% Change'] = df['% Change'].str.replace(',', '', regex=False)  # Remove commas if any
df['% Change'] = pd.to_numeric(df['% Change'], errors='coerce')

# 🔹 Drop rows with NaN in '% Change'
initial_count = len(df)
df = df.dropna(subset=['% Change'])
print(f"Dropped {initial_count - len(df)} rows with invalid percentage values")

# 🔹 Remove extreme outliers for better visualization (optional)
# This doesn't delete them from the dataset, just identifies them for the plot
Q1 = df['% Change'].quantile(0.25)
Q3 = df['% Change'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
outliers = df[(df['% Change'] < lower_bound) | (df['% Change'] > upper_bound)]
print(f"Number of outliers: {len(outliers)}")
print(f"Outlier range: below {lower_bound:.2f}% or above {upper_bound:.2f}%")

# 🔹 Check if we have data after cleaning
if len(df) == 0:
    print("No valid data after cleaning. Exiting.")
    exit()

# 🔹 Create enhanced box plot with statistics
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Box plot
box = ax1.boxplot(df['% Change'], 
                   patch_artist=True, 
                   boxprops=dict(facecolor='skyblue', color='black', linewidth=1.5),
                   medianprops=dict(color='red', linewidth=2),
                   whiskerprops=dict(color='black', linewidth=1.5),
                   capprops=dict(color='black', linewidth=1.5),
                   flierprops=dict(marker='o', markerfacecolor='orange', markersize=6, 
                                  markeredgecolor='black', alpha=0.7))

ax1.set_title('BTC Daily Returns Box Plot', fontsize=16, fontweight='bold')
ax1.set_ylabel('Daily Return (%)', fontsize=14)
ax1.set_xlabel('Bitcoin', fontsize=12)
ax1.grid(True, alpha=0.3, linestyle='--')

# Add mean as a green diamond
mean_val = df['% Change'].mean()
ax1.scatter(1, mean_val, color='green', marker='D', s=100, zorder=3, 
           label=f'Mean: {mean_val:.2f}%')
ax1.legend()

# Histogram with KDE
ax2.hist(df['% Change'], bins=50, alpha=0.7, color='skyblue', edgecolor='black', density=True)
ax2.set_title('Distribution of Daily Returns', fontsize=16, fontweight='bold')
ax2.set_xlabel('Daily Return (%)', fontsize=14)
ax2.set_ylabel('Density', fontsize=14)
ax2.grid(True, alpha=0.3, linestyle='--')

# Add vertical lines for mean and median
ax2.axvline(mean_val, color='green', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}%')
ax2.axvline(df['% Change'].median(), color='red', linestyle='--', linewidth=2, label=f'Median: {df["% Change"].median():.2f}%')
ax2.legend()

plt.tight_layout()
plt.show()

# 🔹 Print comprehensive statistics
print("\n" + "="*50)
print("BITCOIN DAILY RETURNS STATISTICS")
print("="*50)
print(f"Number of data points: {len(df):,}")
print(f"Date range: {df.index[0]} to {df.index[-1]}" if 'Date' in df.columns else "Date column not available")
print(f"\nCentral Tendency:")
print(f"  Mean daily return: {mean_val:.4f}%")
print(f"  Median daily return: {df['% Change'].median():.4f}%")
print(f"  Mode: {df['% Change'].mode().iloc[0]:.4f}%" if not df['% Change'].mode().empty else "  Mode: N/A")
print(f"\nDispersion:")
print(f"  Standard deviation: {df['% Change'].std():.4f}%")
print(f"  Variance: {df['% Change'].var():.4f}")
print(f"  IQR: {IQR:.4f}%")
print(f"\nRange:")
print(f"  Minimum: {df['% Change'].min():.4f}%")
print(f"  Maximum: {df['% Change'].max():.4f}%")
print(f"  Range: {df['% Change'].max() - df['% Change'].min():.4f}%")
print(f"\nPercentiles:")
for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
    print(f"  {p}th: {df['% Change'].quantile(p/100):.4f}%")
print(f"\nSkewness: {df['% Change'].skew():.4f}")
print(f"Kurtosis: {df['% Change'].kurtosis():.4f}")
print("="*50)

# Optional: Save the cleaned data
# df.to_csv('Bitcoin_Cleaned_Data.csv', index=False)
# print("\nCleaned data saved to 'Bitcoin_Cleaned_Data.csv'")