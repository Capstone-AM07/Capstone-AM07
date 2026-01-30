import pandas as pd
import matplotlib.pyplot as plt

# cols
load_col = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Temperature', 'Relative Humidity', 'GHI']
keep_col = ['Date', 'Time', 'Temperature', 'Relative Humidity', 'GHI']

file_list = ['DS_2016.csv', 'DS_2017.csv','DS_2018.csv', 'DS_2019.csv', 'DS_2020.csv']
processed_dfs = []

# file process loop
for file in file_list:
    # raws
    df = pd.read_csv(file, skiprows=2, usecols=load_col)
    
    # date time cols
    temp_ts = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    df['Date'] = temp_ts.dt.date
    df['Time'] = temp_ts.dt.time
    
    # Filter columns
    filtered_df = df[keep_col]
    
    # --- EXPORT INDIVIDUAL YEAR ---
    output_name = f"Filtered_{file}"
    filtered_df.to_csv(output_name, index=False)
    print(f"Saved individual year: {output_name}")
    
    # add 2 list
    processed_dfs.append(filtered_df)

# combine list
final_export = pd.concat(processed_dfs, ignore_index=True)

# export
final_export.to_csv('Combined_Solar_Data_2016_2020.csv', index=False)
print("Saved file")

# ---------------------------------------------------------
# 6. DATA QUALITY TESTS (on combined data)
# ---------------------------------------------------------
print("\n--- DATA QUALITY TEST RESULTS ---")

# Check for Nulls
print(f"Total NaN/Null values: {final_export.isnull().sum().sum()}")

# Check for Impossible Humidity
bad_hum = final_export[(final_export['Relative Humidity'] > 100) | (final_export['Relative Humidity'] < 0)]
print(f"Impossible Humidity rows: {len(bad_hum)}")

# Midnight Sun Check (GHI should be 0)
night_mask = (final_export['Time'] >= pd.to_datetime('00:00:00').time()) & \
             (final_export['Time'] <= pd.to_datetime('03:00:00').time())
strange_night_ghi = final_export[night_mask & (final_export['GHI'] > 0)]
print(f"Strange night-time GHI detections: {len(strange_night_ghi)}")

# Visual Test
plt.figure(figsize=(10, 5))
final_export[['Temperature', 'GHI']].boxplot()
plt.title("Visual Detection of Outliers (Combined Data)")

plt.show()

print("\nAll tasks complete.")