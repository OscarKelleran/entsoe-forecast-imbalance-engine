import os
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

# 1. Environment & API Setup
load_dotenv()
api_key = os.getenv("ENTSOE_API_KEY")
client = EntsoePandasClient(api_key=api_key)

country_code = "NL"
start = pd.Timestamp("20260901", tz="Europe/Brussels")
end = pd.Timestamp("20260908", tz="Europe/Brussels")

# 2. Data Queries
generation = client.query_generation(country_code, start=start, end=end)
prices = client.query_day_ahead_prices(country_code, start=start, end=end)
imbalance_data = client.query_imbalance_prices(country_code, start=start, end=end)
forecast = client.query_wind_and_solar_forecast(country_code, start=start, end=end)

# 3. Compute Metrics
wind_total = (
    generation[("Wind Onshore", "Actual Aggregated")]
    + generation[("Wind Offshore", "Actual Aggregated")]
)
wind_forecast_total = forecast["Wind Onshore"] + forecast["Wind Offshore"]
wind_forecast_error = wind_total - wind_forecast_total

# Resample 15-minute imbalance data to hourly
imbalance_hourly = imbalance_data["Short"].resample("1h").mean()

#Consolidate into a Single Aligned DataFrame
df = pd.DataFrame({
    "wind_error": wind_forecast_error,
    "dam_price": prices,
    "imbalance_price": imbalance_hourly
}).dropna()

# Calculate Spread & Hour directly in the DataFrame
df["spread"] = df["imbalance_price"] - df["dam_price"]
df["hour"] = df.index.hour

print("Aligned sample data:")
print(df.head())

#SQL
import sqlite3
conn = sqlite3.connect("energy_pipeline.db")
df.to_sql("hourly_market_metrics", conn, if_exists="replace", index=True, index_label="timestamp")
conn.close()

# 5. Visualization
fig, ax = plt.subplots(figsize=(9, 6))
scatter = ax.scatter(
    df["wind_error"],
    df["spread"],
    c=df["hour"],
    cmap="viridis",
    alpha=0.7
)

ax.axhline(0, color="red", linestyle="--", linewidth=1, label="Zero Spread (Imbalance = DAM)")

ax.set_xlabel("Wind Forecast Error (Actual - Forecast) [MW]")
ax.set_ylabel("Price Spread: Imbalance - Day-Ahead [EUR/MWh]")
ax.set_title("Forecast Shock Pass-Through: Wind Error vs. Imbalance Spread (NL)")
plt.colorbar(scatter, label="Hour of Day (UTC/CET)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()
os.makedirs("assets", exist_ok=True)
plt.savefig("assets/forecast_error_vs_spread.png", dpi=300, bbox_inches="tight")
plt.show()