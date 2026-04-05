import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 🔹 Set style for better looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# 🔹 Load the CSV
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"
df = pd.read_csv(file_path)

# 🔹 Clean column names
df.columns = df.columns.str.strip()

# 🔹 Check if '% Change' column exists
if '% Change' not in df.columns:
    # Try common alternatives
    possible_names = ['Change %', 'Change', '%Change', 'Percent Change', 'Returns']
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

# 🔹 Convert '% Change' to numeric
df['% Change'] = df['% Change'].astype(str).str.strip()
df['% Change'] = df['% Change'].str.replace('%', '', regex=False)
df['% Change'] = df['% Change'].str.replace(',', '', regex=False)  # Remove commas
df['% Change'] = pd.to_numeric(df['% Change'], errors='coerce')

# 🔹 Drop rows with NaN in '% Change'
initial_count = len(df)
df = df.dropna(subset=['% Change'])
print(f"Removed {initial_count - len(df)} rows with invalid data")
print(f"Remaining data points: {len(df):,}")

# 🔹 Check if we have data after cleaning
if df.empty:
    print("No valid data after cleaning. Exiting.")
    exit()

# 🔹 Create enhanced KDE plot with statistics
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# KDE plot with rug plot
sns.kdeplot(data=df['% Change'], fill=True, color='skyblue', 
            linewidth=2, alpha=0.5, ax=ax1, label='Density')
sns.rugplot(data=df['% Change'], color='navy', height=0.05, alpha=0.3, ax=ax1)

# Add mean and median lines
mean_val = df['% Change'].mean()
median_val = df['% Change'].median()
ax1.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
           label=f'Mean: {mean_val:.2f}%')
ax1.axvline(median_val, color='green', linestyle='--', linewidth=2, 
           label=f'Median: {median_val:.2f}%')

# Shade areas for positive and negative returns
positive_mask = df['% Change'] >= 0
negative_mask = df['% Change'] < 0

if len(df[positive_mask]) > 0:
    sns.kdeplot(data=df[positive_mask]['% Change'], fill=True, 
                color='green', alpha=0.3, linewidth=0, ax=ax1, label='Positive Returns')
if len(df[negative_mask]) > 0:
    sns.kdeplot(data=df[negative_mask]['% Change'], fill=True, 
                color='red', alpha=0.3, linewidth=0, ax=ax1, label='Negative Returns')

ax1.set_title('BTC Daily Returns Distribution (KDE)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Daily Return (%)', fontsize=12)
ax1.set_ylabel('Density', fontsize=12)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3, linestyle='--')

# Second plot: Box plot with KDE overlay
sns.boxplot(data=df['% Change'], ax=ax2, color='skyblue', width=0.3, fliersize=4)
ax2.set_title('BTC Daily Returns Box Plot', fontsize=14, fontweight='bold')
ax2.set_xlabel('Bitcoin', fontsize=12)
ax2.set_ylabel('Daily Return (%)', fontsize=12)
ax2.grid(True, alpha=0.3, linestyle='--', axis='y')

plt.tight_layout()
plt.show()

# 🔹 Print detailed statistics
print("\n" + "="*60)
print("BITCOIN DAILY RETURNS - STATISTICAL SUMMARY")
print("="*60)
print(f"Sample Size: {len(df):,}")
print(f"\nCentral Tendency:")
print(f"  Mean:     {mean_val:.4f}%")
print(f"  Median:   {median_val:.4f}%")
print(f"  Mode:     {df['% Change'].mode().iloc[0]:.4f}%" if not df['% Change'].mode().empty else "  Mode:     N/A")
print(f"\nDispersion:")
print(f"  Std Dev:  {df['% Change'].std():.4f}%")
print(f"  Variance: {df['% Change'].var():.4f}")
print(f"  IQR:      {df['% Change'].quantile(0.75) - df['% Change'].quantile(0.25):.4f}%")
print(f"\nRange:")
print(f"  Min:      {df['% Change'].min():.4f}%")
print(f"  Max:      {df['% Change'].max():.4f}%")
print(f"  Range:    {df['% Change'].max() - df['% Change'].min():.4f}%")
print(f"\nReturn Characteristics:")
print(f"  Positive Days: {len(df[df['% Change'] > 0]):,} ({len(df[df['% Change'] > 0])/len(df)*100:.1f}%)")
print(f"  Negative Days: {len(df[df['% Change'] < 0]):,} ({len(df[df['% Change'] < 0])/len(df)*100:.1f}%)")
print(f"  Neutral Days:  {len(df[df['% Change'] == 0]):,} ({len(df[df['% Change'] == 0])/len(df)*100:.1f}%)")
print(f"\nDistribution Shape:")
print(f"  Skewness: {df['% Change'].skew():.4f} (Negative = left-tailed, Positive = right-tailed)")
print(f"  Kurtosis: {df['% Change'].kurtosis():.4f} (Normal = 0, Heavy tails > 0)")
print("="*60)

# 🔹 Check for normality (optional)
from scipy import stats
statistic, p_value = stats.normaltest(df['% Change'])
print(f"\nNormality Test (D'Agostino's K^2):")
print(f"  Test Statistic: {statistic:.4f}")
print(f"  P-value: {p_value:.4e}")
if p_value < 0.05:
    print("  Conclusion: Data is NOT normally distributed (p < 0.05)")
else:
    print("  Conclusion: Data appears to be normally distributed (p ≥ 0.05)")
print("="*60)