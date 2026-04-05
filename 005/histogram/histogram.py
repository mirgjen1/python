import numpy as np
import matplotlib.pyplot as plt

# 🔹 Generate synthetic daily returns (for illustration)
np.random.seed(42)
daily_returns = np.random.normal(loc=0, scale=1, size=1000)  # mean=0%, std=1%

# 🔹 Create histogram
plt.figure(figsize=(10,6))
plt.hist(daily_returns, bins=30, color='skyblue', edgecolor='black')
plt.title('Histogram of Daily Returns', fontsize=16)
plt.xlabel('Daily Return (%)', fontsize=14)
plt.ylabel('Frequency', fontsize=14)
plt.grid(True, alpha=0.3)
plt.show()