import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 🔹 Load the CSV
file_path = r"C:\Users\cisco\Documents\GitHub\python\005\Bitcoin Historical Data.csv"
df = pd.read_csv(file_path)

# 🔹 Clean column names
df.columns = df.columns.str.strip()

# 🔹 Based on your data format, rename columns properly
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

# 🔹 Create additional derived features for better analysis
df['Spread'] = df['High'] - df['Low']  # Daily price range
df['Range %'] = ((df['High'] - df['Low']) / df['Low']) * 100  # Volatility percentage
df['Price_Change'] = df['Price'] - df['Open']  # Absolute price change
df['Volume_M'] = df['Volume'] / 1000000  # Volume in millions

print(f"Processed {len(df)} rows of data")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print("\nFirst few rows:")
print(df.head())

# 🔹 Select columns for correlation
correlation_cols = ['Price', 'Open', 'High', 'Low', 'Volume', 'Change %', 
                   'Spread', 'Range %', 'Price_Change', 'Volume_M']

# Filter only columns that exist
correlation_cols = [col for col in correlation_cols if col in df.columns]

# 🔹 Create correlation matrix
correlation_matrix = df[correlation_cols].corr()

# 🔹 Create a beautiful correlation heatmap
fig, ax = plt.subplots(figsize=(12, 10))

# Custom colormap (red for negative, blue for positive correlations)
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# Create heatmap with annotations
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))  # Mask for upper triangle
heatmap = sns.heatmap(correlation_matrix, 
                      mask=mask,
                      annot=True,  # Show correlation values
                      fmt='.2f',   # 2 decimal places
                      cmap=cmap,
                      center=0,
                      square=True,
                      linewidths=1,
                      cbar_kws={"shrink": 0.8, "label": "Correlation Coefficient"},
                      annot_kws={'size': 10, 'weight': 'bold'},
                      ax=ax)

# Customize the plot
plt.title('Bitcoin Market Correlation Heatmap', fontsize=18, fontweight='bold', pad=20)
plt.xticks(rotation=45, ha='right', fontsize=11)
plt.yticks(rotation=0, fontsize=11)

# Adjust layout
plt.tight_layout()
plt.show()

# 🔹 Create a more detailed heatmap with clustering
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Heatmap 1: Standard correlation
sns.heatmap(correlation_matrix, 
            annot=True, 
            fmt='.2f', 
            cmap='coolwarm', 
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax1)
ax1.set_title('Standard Correlation Matrix', fontsize=14, fontweight='bold')
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')

# Heatmap 2: Clustered correlation (groups similar correlations together)
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform

# Calculate linkage for clustering
distance_matrix = 1 - abs(correlation_matrix)
linkage_matrix = linkage(squareform(distance_matrix), method='average')

# Get order of clusters
from scipy.cluster.hierarchy import leaves_list
order = leaves_list(linkage_matrix)
clustered_matrix = correlation_matrix.iloc[order, order]

sns.heatmap(clustered_matrix, 
            annot=True, 
            fmt='.2f', 
            cmap='RdYlBu_r', 
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax2)
ax2.set_title('Clustered Correlation Matrix', fontsize=14, fontweight='bold')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()

# 🔹 Create a correlation bar chart (top correlations with Price)
fig3, ax3 = plt.subplots(figsize=(10, 6))

# Get correlations with Price
price_corr = correlation_matrix['Price'].drop('Price').sort_values(ascending=False)

# Create bar chart
colors = ['green' if x > 0 else 'red' for x in price_corr.values]
bars = ax3.bar(range(len(price_corr)), price_corr.values, color=colors, alpha=0.7, edgecolor='black')
ax3.set_xticks(range(len(price_corr)))
ax3.set_xticklabels(price_corr.index, rotation=45, ha='right')
ax3.set_ylabel('Correlation with Price', fontsize=12)
ax3.set_title('Variables Most Correlated with Bitcoin Price', fontsize=14, fontweight='bold')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax3.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, price_corr.values)):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (0.02 if val > 0 else -0.08),
             f'{val:.2f}', ha='center', va='bottom' if val > 0 else 'top', fontweight='bold')

plt.tight_layout()
plt.show()

# 🔹 Print detailed correlation analysis
print("\n" + "="*70)
print("CORRELATION ANALYSIS - KEY INSIGHTS")
print("="*70)

# Find strongest positive and negative correlations
corr_pairs = []
for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        corr_pairs.append({
            'variables': f"{correlation_matrix.columns[i]} & {correlation_matrix.columns[j]}",
            'correlation': correlation_matrix.iloc[i, j]
        })

corr_pairs = sorted(corr_pairs, key=lambda x: abs(x['correlation']), reverse=True)

print("\n🔹 TOP 5 STRONGEST CORRELATIONS:")
for i, pair in enumerate(corr_pairs[:5], 1):
    strength = "Very Strong" if abs(pair['correlation']) > 0.8 else "Strong" if abs(pair['correlation']) > 0.6 else "Moderate"
    direction = "Positive" if pair['correlation'] > 0 else "Negative"
    print(f"  {i}. {pair['variables']}: {pair['correlation']:.3f} ({direction} - {strength})")

print("\n🔹 CORRELATIONS WITH DAILY RETURNS (Change %):")
if 'Change %' in correlation_matrix.columns:
    returns_corr = correlation_matrix['Change %'].sort_values(ascending=False)
    for var, corr in returns_corr.items():
        if var != 'Change %':
            print(f"  • {var}: {corr:.3f}")

print("\n🔹 CORRELATIONS WITH VOLUME:")
if 'Volume' in correlation_matrix.columns:
    volume_corr = correlation_matrix['Volume'].sort_values(ascending=False)
    for var, corr in volume_corr.items():
        if var != 'Volume':
            print(f"  • {var}: {corr:.3f}")

print("\n🔹 CORRELATIONS WITH VOLATILITY (Range %):")
if 'Range %' in correlation_matrix.columns:
    volatility_corr = correlation_matrix['Range %'].sort_values(ascending=False)
    for var, corr in volatility_corr.items():
        if var != 'Range %':
            print(f"  • {var}: {corr:.3f}")

print("\n" + "="*70)

# 🔹 Create a correlation network graph (optional - requires networkx)
try:
    import networkx as nx
    
    fig4, ax4 = plt.subplots(figsize=(12, 10))
    
    # Create graph
    G = nx.Graph()
    
    # Add nodes
    for node in correlation_matrix.columns:
        G.add_node(node)
    
    # Add edges with correlation > 0.5 or < -0.5
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_val = correlation_matrix.iloc[i, j]
            if abs(corr_val) > 0.5:  # Only show strong correlations
                G.add_edge(correlation_matrix.columns[i], 
                          correlation_matrix.columns[j], 
                          weight=abs(corr_val),
                          color='green' if corr_val > 0 else 'red')
    
    # Draw the graph
    pos = nx.spring_layout(G, k=2, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=1500, node_color='lightblue', 
                          node_shape='o', alpha=0.7)
    
    # Draw edges with colors based on correlation sign
    edges_positive = [(u, v) for (u, v, d) in G.edges(data=True) if d['color'] == 'green']
    edges_negative = [(u, v) for (u, v, d) in G.edges(data=True) if d['color'] == 'red']
    
    nx.draw_networkx_edges(G, pos, edgelist=edges_positive, width=2, alpha=0.6, edge_color='green')
    nx.draw_networkx_edges(G, pos, edgelist=edges_negative, width=2, alpha=0.6, edge_color='red')
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    ax4.set_title('Correlation Network (|r| > 0.5)', fontsize=14, fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.show()
    
except ImportError:
    print("\nNote: Install 'networkx' for network graph visualization: pip install networkx")

print("\n✅ Correlation analysis complete!")