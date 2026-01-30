import pandas as pd
import os

# --- SETTINGS ---
output_filename = 'Combined_Filtered_Building_Load.csv'
start_date = '2018-01-01'
end_date = '2020-12-31'

processed_dfs = []

# Get all CSV files in the current directory
# Added a check to skip the output file if it already exists
file_list = [f for f in os.listdir('.') if f.endswith('.csv') and f != output_filename]

if not file_list:
    print("No CSV files found in the current directory.")
else:
    print(f"Found {len(file_list)} files. Starting processing...")

    for file in file_list:
        try:
            # utf-8-sig handles the Â mismatch; sep=None auto-detects commas vs tabs
            # If your files have the 9-line header, add: skiprows=9
            df = pd.read_csv(file, sep=None, engine='python', encoding='utf-8-sig')

            # --- STEP 1: FUZZY COLUMN SEARCH ---
            # Search for 'date' or 'time'
            date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
            # Search for 'power' (ignoring stats like std/min/max)
            power_cols = [c for c in df.columns if 'power' in c.lower() and 
                          not any(x in c.lower() for x in ['std', 'min', 'max', 'deviation'])]

            if not date_cols or not power_cols:
                print(f"Skipping {file}: Could not find clear Date or Power columns.")
                continue
            
            date_col = date_cols[0]
            power_col = power_cols[0]

            # --- STEP 2: DATE CONVERSION AND FILTERING ---
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Drop rows where date conversion failed (like header text or corrupt data)
            df = df.dropna(subset=[date_col])

            # Filter for 2018 to 2020
            mask = (df[date_col] >= start_date) & (df[date_col] <= end_date)
            df_filtered = df.loc[mask, [date_col, power_col]].copy()

            if df_filtered.empty:
                print(f"No data within 2018-2020 found in {file}")
                continue

            # Rename for a clean combined file
            df_filtered = df_filtered.rename(columns={
                date_col: 'DateTime',
                power_col: 'RealPower_kW'
            })

            # Add source filename to track the building/source
            df_filtered['Source_File'] = file
            
            processed_dfs.append(df_filtered)
            print(f"Successfully processed {len(df_filtered)} rows from {file}")

        except Exception as e:
            print(f"Error processing {file}: {e}")

    # --- STEP 3: CONCATENATE AND EXPORT ---
    if processed_dfs:
        final_df = pd.concat(processed_dfs, ignore_index=True)
        # Ensure the output is sorted by time
        final_df = final_df.sort_values(by='DateTime')
        
        final_df.to_csv(output_filename, index=False)
        print(f"\nSUCCESS!")
        print(f"Processed {len(file_list)} files.")
        print(f"Final output: {output_filename} ({len(final_df)} total rows)")
    else:
        print("\nNo data matched your filtering criteria.")