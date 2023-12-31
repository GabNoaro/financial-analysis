from secret import api_key  # Create a "secret.py" file with your API Key and import it
import pandas as pd
import requests
import os

# Define the base URL for Financial Modeling Prep API
base_url = 'https://financialmodelingprep.com/api/v3/'

# Define the symbols for the selected tickers
symbols_str = 'AMKR,FORM,RMBS,LSCC,MTSI,ALGM,WOLF,QRVO,IPGP,POWI,SYNA'
symbols = symbols_str.split(',')

# Define the directory to store pickle files
pickle_dir = 'financial_data_pickle'
os.makedirs(pickle_dir, exist_ok=True)

# Create dictionaries to hold data for each financial statement, symbol, and profile
dcf = {}
rating = {}
key_metrics = {}
growth = {}

# Loop through each symbol
for symbol in symbols:
    # Create empty DataFrames for each financial statement

    dcf_df = pd.DataFrame()
    rating_df = pd.DataFrame()
    key_metrics_df = pd.DataFrame()
    growth_df = pd.DataFrame()

    # Define the other company data we want to import
    data1 = ['discounted-cash-flow', 'rating']
    data2 = ['key-metrics', 'financial-growth']

    # Loop through each company data type
    for data_type in data1:
        pickle_filename = f'{pickle_dir}/{symbol}_{data_type}.pkl'

        try:
            # Load the DataFrame from the pickle file
            df = pd.read_pickle(pickle_filename)

        except FileNotFoundError:
            # If the pickle file is not found, make the API request and save the DataFrame to a pickle file
            url_data = f'{base_url}{data_type}/{symbol}?apikey={api_key}'
            response_statement = requests.get(url_data)

            if response_statement.status_code == 200:
                data = response_statement.json()
                df = pd.DataFrame(data)
                df.to_pickle(pickle_filename)

        # Transpose the DataFrame
        #df = df.transpose()

        # Store the DataFrame in the appropriate dictionary
        if data_type == 'discounted-cash-flow':
            dcf[symbol] = df
        elif data_type == 'rating':
            rating[symbol] = df

    for data_type in data2:
        pickle_filename = f'{pickle_dir}/{symbol}_{data_type}.pkl'

        try:
            # Load the DataFrame from the pickle file
            df = pd.read_pickle(pickle_filename)

        except FileNotFoundError:
            # If the pickle file is not found, make the API request and save the DataFrame to a pickle file
            period = 'annual'  # Select between annual and quarter
            url_data = f'{base_url}{data_type}/{symbol}?period={period}&apikey={api_key}'
            response_statement = requests.get(url_data)

            if response_statement.status_code == 200:
                data = response_statement.json()
                df = pd.DataFrame(data)
                df.to_pickle(pickle_filename)

        # Transpose the DataFrame
        #df = df.transpose()

        # Store the DataFrame in the appropriate dictionary
        if data_type == 'key-metrics':
            key_metrics[symbol] = df
        elif data_type == 'financial-growth':
            growth[symbol] = df

# Merge the DataFrames on the 'symbol' column
stock_screener_dfs = []  # Use a list to store individual DataFrames

for symbol in symbols:
    # Load data for each type
    dcf_filename = f'{pickle_dir}/{symbol}_discounted-cash-flow.pkl'
    rating_filename = f'{pickle_dir}/{symbol}_rating.pkl'
    key_metrics_filename = f'{pickle_dir}/{symbol}_key-metrics.pkl'
    growth_filename = f'{pickle_dir}/{symbol}_financial-growth.pkl'

    # Load DataFrames from pickle files
    dcf_df = pd.read_pickle(dcf_filename)
    rating_df = pd.read_pickle(rating_filename)
    key_metrics_df = pd.read_pickle(key_metrics_filename)
    growth_df = pd.read_pickle(growth_filename)

    # Append individual DataFrames to the list
    stock_screener_dfs.append(dcf_df)
    stock_screener_dfs.append(rating_df)
    stock_screener_dfs.append(key_metrics_df)
    stock_screener_dfs.append(growth_df)




# Concatenate the list of DataFrames into the final DataFrame
stock_screener_df = pd.concat(stock_screener_dfs, ignore_index=True)

# Reset the index
stock_screener_df.reset_index(drop=True, inplace=True)

# Print the merged DataFrame
print(stock_screener_df)

# Save the merged DataFrame to CSV
stock_screener_df.to_csv(f'deliverables/stock_screener_with_dates_for_{symbols_str}.csv', index=False)

# Convert 'date' to datetime format
stock_screener_df['date'] = pd.to_datetime(stock_screener_df['date'])

# Group by 'symbol' and 'date', then keep the first non-null value for each group
grouped_df = stock_screener_df.groupby(['symbol', stock_screener_df['date'].dt.year], as_index=False).first()
# Replace blank cells with 0
grouped_df = grouped_df.fillna(0)

# Print the grouped DataFrame
print(grouped_df)

# Save the grouped DataFrame to CSV
grouped_df.to_csv(f'deliverables/stock_screener_grouped_for_{symbols_str}.csv', index=False)
