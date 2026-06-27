
import time
import akshare as ak

symbol = "600519"

t0 = time.perf_counter()
df = ak.stock_zh_a_hist(
    symbol=symbol,
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="",
)
elapsed = time.perf_counter() - t0

print(f"=== 抓取耗时: {elapsed:.2f}s ===")
print(f"shape: {df.shape}")
print(f"\n--- dtypes ---\n{df.dtypes}")
print(f"\n--- head(3) ---\n{df.head(3)}")
print(f"\n--- tail(3) ---\n{df.tail(3)}")
