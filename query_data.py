import sqlite3
import pandas as pd

conn = sqlite3.connect("energy_pipeline.db")

sql_query = """
    SELECT timestamp, wind_error, spread, dam_price, imbalance_price
    FROM hourly_market_metrics
    WHERE wind_error < 0
    ORDER BY spread DESC
    LIMIT 5;
"""

top_spikes = pd.read_sql_query(sql_query, conn)
conn.close()

print("Top 5 Wind Shortfall Price Spikes:")
print(top_spikes)