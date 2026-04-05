import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')  # Suppress minor warnings

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
        # Convert to string first, handle potential NaN
        df[col] = df[col].astype(str)
        df[col] = df[col].str.replace(',', '', regex=False)
        df[col] = df[col].str.replace('%', '', regex=False)
        df[col] = df[col].str.replace('K', '000', regex=False)  # Handle 'K' suffix
        df[col] = df[col].str.replace('M', '000000', regex=False)  # Handle 'M' suffix
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 🔹 Convert Date column and sort
if 'Date' in df.columns:
    # Try multiple date formats
    try:
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    except:
        try:
            df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
        except:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.sort_values('Date').reset_index(drop=True)

# 🔹 Drop rows with NaN in essential columns
essential_cols = ['Price', 'Change %'] if 'Change %' in df.columns else ['Price']
df = df.dropna(subset=essential_cols)

# Check if we have data
if len(df) < 10:
    print(f"Error: Only {len(df)} rows of valid data. Need at least 10 rows.")
    print("Available columns:", df.columns.tolist())
    print("\nFirst few rows of raw data:")
    print(df.head())
    exit()

print(f"✅ Processed {len(df)} rows of data")
print(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"📊 Available columns: {df.columns.tolist()}")
print("\nFirst few rows:")
print(df[['Date', 'Price'] + (['Change %'] if 'Change %' in df.columns else [])].head())

# Check if Change % column exists
if 'Change %' not in df.columns:
    print("\n⚠️ 'Change %' column not found. Calculating from Price column...")
    df['Change %'] = df['Price'].pct_change() * 100
    print("✅ Calculated daily returns from Price column")

# 🔹 Create lag plots for different variables and lags
# Define which variables to analyze
available_vars = []
if 'Change %' in df.columns:
    available_vars.append('Change %')
if 'Price' in df.columns:
    available_vars.append('Price')
if 'Volume' in df.columns:
    available_vars.append('Volume')

# 1. LAG PLOT FOR DAILY RETURNS (Change %)
if 'Change %' in df.columns:
    fig1, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig1.suptitle('Bitcoin Daily Returns - Lag Plots', fontsize=16, fontweight='bold')
    
    lags = [1, 2, 3, 5, 7, 14]  # Different lag values to analyze
    for i, lag in enumerate(lags):
        if i >= 6: break
        row = i // 3
        col = i % 3
        
        # Create lagged values
        returns = df['Change %'].values
        if len(returns) <= lag:
            axes[row, col].text(0.5, 0.5, f'Insufficient data for lag {lag}', 
                               ha='center', va='center')
            continue
            
        lagged_returns = np.roll(returns, lag)
        
        # Remove the first 'lag' points to avoid autocorrelation artifacts
        returns_plot = returns[lag:]
        lagged_plot = lagged_returns[lag:]
        
        # Scatter plot
        axes[row, col].scatter(lagged_plot, returns_plot, alpha=0.5, s=20, c='steelblue')
        
        # Add reference line (y=x)
        min_val = min(returns_plot.min(), lagged_plot.min())
        max_val = max(returns_plot.max(), lagged_plot.max())
        axes[row, col].plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='y=x')
        
        # Add horizontal and vertical zero lines
        axes[row, col].axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        axes[row, col].axvline(x=0, color='gray', linestyle='-', alpha=0.3)
        
        # Calculate correlation
        try:
            corr = np.corrcoef(lagged_plot, returns_plot)[0, 1]
            if np.isnan(corr):
                corr = 0
        except:
            corr = 0
        
        axes[row, col].set_title(f'Lag = {lag} day(s) (r = {corr:.3f})', fontsize=11)
        axes[row, col].set_xlabel(f'Return (t-{lag}) %', fontsize=10)
        axes[row, col].set_ylabel('Return (t) %', fontsize=10)
        axes[row, col].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
else:
    print("⚠️ Skipping returns lag plots - 'Change %' column not available")

# 2. LAG PLOT FOR PRICE
if 'Price' in df.columns:
    fig2, axes2 = plt.subplots(2, 3, figsize=(15, 10))
    fig2.suptitle('Bitcoin Price - Lag Plots', fontsize=16, fontweight='bold')
    
    for i, lag in enumerate(lags):
        if i >= 6: break
        row = i // 3
        col = i % 3
        
        # Create lagged values
        prices = df['Price'].values
        if len(prices) <= lag:
            axes2[row, col].text(0.5, 0.5, f'Insufficient data for lag {lag}', 
                               ha='center', va='center')
            continue
            
        lagged_prices = np.roll(prices, lag)
        
        # Remove the first 'lag' points
        prices_plot = prices[lag:]
        lagged_plot = lagged_prices[lag:]
        
        # Scatter plot
        axes2[row, col].scatter(lagged_plot, prices_plot, alpha=0.5, s=20, c='green')
        
        # Add reference line
        min_val = min(prices_plot.min(), lagged_plot.min())
        max_val = max(prices_plot.max(), lagged_plot.max())
        axes2[row, col].plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5)
        
        # Calculate correlation
        try:
            corr = np.corrcoef(lagged_plot, prices_plot)[0, 1]
            if np.isnan(corr):
                corr = 0
        except:
            corr = 0
        
        axes2[row, col].set_title(f'Lag = {lag} day(s) (r = {corr:.3f})', fontsize=11)
        axes2[row, col].set_xlabel(f'Price (t-{lag}) USD', fontsize=10)
        axes2[row, col].set_ylabel('Price (t) USD', fontsize=10)
        axes2[row, col].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
else:
    print("⚠️ Skipping price lag plots - 'Price' column not available")

# 3. LAG PLOT FOR VOLUME
if 'Volume' in df.columns:
    fig3, axes3 = plt.subplots(2, 3, figsize=(15, 10))
    fig3.suptitle('Bitcoin Volume - Lag Plots', fontsize=16, fontweight='bold')
    
    for i, lag in enumerate(lags):
        if i >= 6: break
        row = i // 3
        col = i % 3
        
        # Create lagged values
        volumes = df['Volume'].values
        if len(volumes) <= lag:
            axes3[row, col].text(0.5, 0.5, f'Insufficient data for lag {lag}', 
                               ha='center', va='center')
            continue
            
        lagged_volumes = np.roll(volumes, lag)
        
        # Remove the first 'lag' points
        volumes_plot = volumes[lag:]
        lagged_plot = lagged_volumes[lag:]
        
        # Scatter plot
        axes3[row, col].scatter(lagged_plot, volumes_plot, alpha=0.5, s=20, c='orange')
        
        # Add reference line
        min_val = min(volumes_plot.min(), lagged_plot.min())
        max_val = max(volumes_plot.max(), lagged_plot.max())
        axes3[row, col].plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5)
        
        # Calculate correlation
        try:
            corr = np.corrcoef(lagged_plot, volumes_plot)[0, 1]
            if np.isnan(corr):
                corr = 0
        except:
            corr = 0
        
        axes3[row, col].set_title(f'Lag = {lag} day(s) (r = {corr:.3f})', fontsize=11)
        axes3[row, col].set_xlabel(f'Volume (t-{lag})', fontsize=10)
        axes3[row, col].set_ylabel('Volume (t)', fontsize=10)
        axes3[row, col].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
else:
    print("⚠️ Skipping volume lag plots - 'Volume' column not available")

# 4. COMPREHENSIVE LAG ANALYSIS WITH AUTOCORRELATION
if len(available_vars) > 0:
    fig4, axes4 = plt.subplots(1, len(available_vars), figsize=(5*len(available_vars), 5))
    if len(available_vars) == 1:
        axes4 = [axes4]
    fig4.suptitle('Autocorrelation Analysis (0-30 lags)', fontsize=14, fontweight='bold')
    
    colors = {'Change %': 'steelblue', 'Price': 'green', 'Volume': 'orange'}
    
    for idx, var in enumerate(available_vars):
        # Calculate autocorrelation for different lags
        max_lag = min(30, len(df) // 2)  # Don't exceed half the data length
        autocorr_values = []
        
        for lag in range(max_lag + 1):
            if lag == 0:
                autocorr_values.append(1.0)
            else:
                try:
                    original = df[var].values[lag:]
                    lagged = df[var].values[:-lag]
                    corr = np.corrcoef(original, lagged)[0, 1]
                    autocorr_values.append(corr if not np.isnan(corr) else 0)
                except:
                    autocorr_values.append(0)
        
        # Plot autocorrelation function
        axes4[idx].bar(range(max_lag + 1), autocorr_values, color=colors.get(var, 'blue'), 
                      alpha=0.7, edgecolor='black')
        axes4[idx].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Add significance threshold (approximately 2/sqrt(n))
        threshold = 2 / np.sqrt(len(df))
        axes4[idx].axhline(y=threshold, color='red', linestyle='--', alpha=0.5, 
                          label=f'Threshold (±{threshold:.3f})')
        axes4[idx].axhline(y=-threshold, color='red', linestyle='--', alpha=0.5)
        
        axes4[idx].set_xlabel('Lag (days)', fontsize=11)
        axes4[idx].set_ylabel('Autocorrelation', fontsize=11)
        axes4[idx].set_title(f'{var}', fontsize=12, fontweight='bold')
        axes4[idx].grid(True, alpha=0.3)
        axes4[idx].legend(fontsize=8)
    
    plt.tight_layout()
    plt.show()
else:
    print("⚠️ No variables available for autocorrelation analysis")

# 5. ADVANCED: Color-coded lag plot (only if Change % and Volume exist)
if 'Change %' in df.columns and 'Volume' in df.columns:
    fig5, axes5 = plt.subplots(1, 2, figsize=(14, 6))
    fig5.suptitle('Enhanced Lag Plots with Additional Dimensions', fontsize=14, fontweight='bold')
    
    # Plot 1: Returns lag plot colored by volume
    lag = 1
    returns = df['Change %'].values
    lagged_returns = np.roll(returns, lag)
    returns_plot = returns[lag:]
    lagged_plot = lagged_returns[lag:]
    volumes_plot = df['Volume'].values[lag:]
    
    scatter = axes5[0].scatter(lagged_plot, returns_plot, c=volumes_plot, 
                              cmap='viridis', alpha=0.6, s=40, edgecolors='black', linewidth=0.5)
    axes5[0].plot([min(lagged_plot), max(lagged_plot)], [min(lagged_plot), max(lagged_plot)], 
                 'r--', alpha=0.5, label='y=x')
    axes5[0].axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    axes5[0].axvline(x=0, color='gray', linestyle='-', alpha=0.3)
    axes5[0].set_xlabel(f'Return (t-{lag}) %', fontsize=11)
    axes5[0].set_ylabel(f'Return (t) %', fontsize=11)
    axes5[0].set_title(f'Returns Lag Plot (Lag={lag}) - Colored by Volume', fontsize=11)
    axes5[0].grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=axes5[0], label='Volume')
    
    # Plot 2: Returns lag plot with point size based on absolute return
    abs_returns = np.abs(returns_plot)
    scatter2 = axes5[1].scatter(lagged_plot, returns_plot, c=returns_plot, 
                               cmap='RdYlGn', alpha=0.6, s=abs_returns * 10 + 20, 
                               edgecolors='black', linewidth=0.5)
    axes5[1].plot([min(lagged_plot), max(lagged_plot)], [min(lagged_plot), max(lagged_plot)], 
                 'r--', alpha=0.5, label='y=x')
    axes5[1].axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    axes5[1].axvline(x=0, color='gray', linestyle='-', alpha=0.3)
    axes5[1].set_xlabel(f'Return (t-{lag}) %', fontsize=11)
    axes5[1].set_ylabel(f'Return (t) %', fontsize=11)
    axes5[1].set_title(f'Returns Lag Plot (Lag={lag}) - Size = |Return|', fontsize=11)
    axes5[1].grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=axes5[1], label='Return (%)')
    
    plt.tight_layout()
    plt.show()
else:
    print("⚠️ Skipping enhanced lag plots - need both 'Change %' and 'Volume' columns")

# 6. STATISTICAL SUMMARY
print("\n" + "="*70)
print("LAG PLOT ANALYSIS - STATISTICAL SUMMARY")
print("="*70)

if 'Change %' in df.columns:
    print("\n🔹 AUTOCORRELATION OF RETURNS (Change %):")
    for lag in [1, 2, 3, 5, 7, 14, 21, 30]:
        if lag < len(df):
            try:
                original = df['Change %'].values[lag:]
                lagged = df['Change %'].values[:-lag]
                corr = np.corrcoef(original, lagged)[0, 1]
                if np.isnan(corr):
                    corr = 0
                significance = "***" if abs(corr) > 0.2 else "**" if abs(corr) > 0.1 else "*"
                print(f"  Lag {lag:2d}: {corr:.4f} {significance}")
            except:
                print(f"  Lag {lag:2d}: N/A")
    
    # Check for mean reversion in returns
    try:
        lag1_corr = np.corrcoef(df['Change %'].values[1:], df['Change %'].values[:-1])[0, 1]
        if not np.isnan(lag1_corr):
            if lag1_corr < 0:
                print("\n✓ Negative lag-1 correlation suggests MEAN REVERSION in daily returns")
            else:
                print("\n✓ Positive lag-1 correlation suggests TREND FOLLOWING in daily returns")
    except:
        pass

if 'Price' in df.columns:
    print("\n🔹 AUTOCORRELATION OF PRICE:")
    for lag in [1, 2, 3, 5, 7, 14, 21, 30]:
        if lag < len(df):
            try:
                original = df['Price'].values[lag:]
                lagged = df['Price'].values[:-lag]
                corr = np.corrcoef(original, lagged)[0, 1]
                if np.isnan(corr):
                    corr = 0
                print(f"  Lag {lag:2d}: {corr:.4f}")
            except:
                print(f"  Lag {lag:2d}: N/A")
    
    # Check price persistence
    try:
        price_lag1 = np.corrcoef(df['Price'].values[1:], df['Price'].values[:-1])[0, 1]
        if not np.isnan(price_lag1) and price_lag1 > 0.9:
            print("\n✓ Very high price autocorrelation - prices show strong persistence (random walk-like)")
    except:
        pass

if 'Volume' in df.columns:
    print("\n🔹 AUTOCORRELATION OF VOLUME:")
    for lag in [1, 2, 3, 5, 7, 14, 21, 30]:
        if lag < len(df):
            try:
                original = df['Volume'].values[lag:]
                lagged = df['Volume'].values[:-lag]
                corr = np.corrcoef(original, lagged)[0, 1]
                if np.isnan(corr):
                    corr = 0
                print(f"  Lag {lag:2d}: {corr:.4f}")
            except:
                print(f"  Lag {lag:2d}: N/A")
    
    # Check volume clustering
    try:
        volume_lag1 = np.corrcoef(df['Volume'].values[1:], df['Volume'].values[:-1])[0, 1]
        if not np.isnan(volume_lag1) and volume_lag1 > 0.5:
            print("\n✓ Significant volume autocorrelation - indicates volume clustering")
    except:
        pass

print("\n" + "="*70)

# Optional: Save lag plot data to CSV
lag_data = pd.DataFrame({'Lag': range(1, 31)})
for var in available_vars:
    autocorr_list = []
    for lag in range(1, 31):
        if lag < len(df):
            try:
                original = df[var].values[lag:]
                lagged = df[var].values[:-lag]
                corr = np.corrcoef(original, lagged)[0, 1]
                autocorr_list.append(corr if not np.isnan(corr) else np.nan)
            except:
                autocorr_list.append(np.nan)
        else:
            autocorr_list.append(np.nan)
    lag_data[f'{var}_Autocorr'] = autocorr_list

# Uncomment to save
# lag_data.to_csv('Bitcoin_Autocorrelation_Analysis.csv', index=False)
# print("\n✅ Autocorrelation data saved to 'Bitcoin_Autocorrelation_Analysis.csv'")

print("\n✅ Lag plot analysis complete!")