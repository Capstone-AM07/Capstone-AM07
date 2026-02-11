import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the columns for final version
keep_col = ['Date', 'Time', 'Wind speed (m/s)', 'Wind direction', 'Temperature']

file_list = [f for f in os.listdir('.') if f.startswith('Penmanshiel') and f.endswith('.csv')]
processed_dfs = []

for file in file_list:
    try:
        # load file, skip 9 info rows, latin 1 encode for weird symbols
        df = pd.read_csv(file, sep=None, engine='python', encoding='latin-1', skiprows= 9)

        # find cols 
        col_map = {
            'timestamp': [c for c in df.columns if 'Date and time' in c][0],
            'ws1': [c for c in df.columns if 'Wind speed Sensor 1 (m/s)' in c][0],
            'ws2': [c for c in df.columns if 'Wind speed Sensor 2 (m/s)' in c][0],
            'wd': [c for c in df.columns if 'Wind direction' in c and 'Standard deviation' not in c][0],
            'temp': [c for c in df.columns if 'Ambient temperature (converter)' in c][0]
        }

        # Avg s1 + s2
        df['Wind speed (m/s)'] = df[[col_map['ws1'], col_map['ws2']]].mean(axis=1)

        # date time col
        temp_ts = pd.to_datetime(df[col_map['timestamp']])
        df['Date'] = temp_ts.dt.date
        df['Time'] = temp_ts.dt.time

        # clean names
        df = df.rename(columns={
            col_map['wd']: 'Wind direction',
            col_map['temp']: 'Temperature'
        })

        processed_dfs.append(df[keep_col])
        print(f"Successful for: {file}")

    except Exception as e:
        print(f"Skipped {file} due to error: {e}")

# combined file create
if processed_dfs:
    final_export = pd.concat(processed_dfs, ignore_index=True)
    
    # file export
    output_filename = 'Combined_Penmanshiel_Wind_Data.csv'
    final_export.to_csv(output_filename, index=False)
    
    print(f"\nSuccess! Saved {len(final_export)} rows to {output_filename}")
    
    # Visual Quality Check
    plt.figure(figsize=(10, 5))
    final_export[['Wind speed (m/s)', 'Temperature']].boxplot()
    plt.title("Turbine Data Quality Check (Averaged Wind Speed)")
    plt.show()

else:
    print("\nError with cols")