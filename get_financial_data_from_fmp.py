"""
Read if you intend to use this script:
Attribution is required for all users. It is as simple as putting “Data provided by Financial Modeling Prep”
somewhere on your site or app and linking that text to https://financialmodelingprep.com/developer/docs/.
In case of limited screen space, or design constraints, the attribution link can be included in your terms of service.

FUTURE WORK: It doesn't seem possible to specify the period of retrieval for historical market capitalization data from
the Financial Modeling Prep API, which automatically retrieves daily historical data from the most recent date.
If such data is needed, future work may include integrating other APIs in the script or unofficial packages, such as
yFinance, that are however less stable and reliable. However, this script those mix different finacial data request libraries,
to avoid the code to be messy, ovrcomplicated, and difficult to maintain (simplicity is key).
"""

from secret import api_key #Create a "secret.py" file with your API Key and import it
import requests
import pandas as pd
import os

# Define the base URL for Financial Modeling Prep API
base_url = 'https://financialmodelingprep.com/api/v3/'

# Define the symbol for the selected tickers
symbols_str = 'AMKR,FORM,RMBS,LSCC,MTSI,ALGM,WOLF,QRVO,IPGP,POWI,SYNA'
symbols = symbols_str.split(',')

# Define the directory to store pickle files
pickle_dir = 'financial_data_pickle'
os.makedirs(pickle_dir, exist_ok=True)

for symbol in symbols:
    # Create empty DataFrames for each financial statement
    balance_sheet_df = pd.DataFrame()
    income_statement_df = pd.DataFrame()
    cash_flow_statement_df = pd.DataFrame()
    company_profile_df = pd.DataFrame()
    historical_market_cap_df = pd.DataFrame()

    # Define the pickle file name for profile data
    profile_pickle_filename = f'{pickle_dir}/{symbol}_profile_data.pkl'

    try:
        # Try to load the DataFrame from the pickle file
        company_profile_df = pd.read_pickle(profile_pickle_filename)
        print(f'Loaded profile data for {symbol} from {profile_pickle_filename}')

    except FileNotFoundError:
        # If the pickle file is not found, make the API request and save the DataFrame to a pickle file
        limit=0 #this states the limit for the request below
        if limit > 0:
            url_info = f'{base_url}profile/{symbol}?limit={limit}&apikey={api_key}'
            response_info = requests.get(url_info)

            # Check if the request was successful (status code 200)
            if response_info.status_code == 200:
                # Parse the JSON response
                profile_data = response_info.json()

                # Create a DataFrame from the response data
                company_profile_df = pd.DataFrame(profile_data)

                # Save the DataFrame to a pickle file
                company_profile_df.to_pickle(profile_pickle_filename)
                print(f'Saved profile data for {symbol} to {profile_pickle_filename}')

            else:
                # Print an error message if the request was not successful
                print(f'Error fetching profile data for {symbol}. Status code: {response_info.status_code}')

        elif limit == 0:
            print(f'Your limit for the requests on the company profile data is set to {limit}')

        else:
            print(f'Your limit for the API request for the company profile data is not specified or invalid. Limit: {limit}')

    # Loop through each financial statement type
    for statement_type in ['balance-sheet-statement', 'income-statement', 'cash-flow-statement']:
        # Define the pickle file name for statement data
        statement_pickle_filename = f'{pickle_dir}/{symbol}_{statement_type}_data.pkl'

        try:
            # Try to load the DataFrame from the pickle file
            df = pd.read_pickle(statement_pickle_filename)
            print(f'Loaded {statement_type} data for {symbol} from {statement_pickle_filename}')

        except FileNotFoundError:
            # If the pickle file is not found, make the API request and save the DataFrame to a pickle file
            period = 'annual' #choose between 'annual' and 'quarter'
            url_statement = f'{base_url}{statement_type}/{symbol}?period={period}&apikey={api_key}'
            response_statement = requests.get(url_statement)

            # Check if the request was successful (status code 200)
            if response_statement.status_code == 200:
                # Parse the JSON response
                statement_data = response_statement.json()

                # Create a DataFrame from the response data
                df = pd.DataFrame(statement_data)

                # Save the DataFrame to a pickle file
                df.to_pickle(statement_pickle_filename)
                print(f'Saved {statement_type} data for {symbol} to {statement_pickle_filename}')

            else:
                # Print an error message if the request was not successful
                print(f'Error fetching {statement_type} data for {symbol}. Status code: {response_statement.status_code}')

        # Store the DataFrame in the appropriate variable based on statement type
        if statement_type == 'balance-sheet-statement':
            balance_sheet_df = df
        elif statement_type == 'income-statement':
            income_statement_df = df
        elif statement_type == 'cash-flow-statement':
            cash_flow_statement_df = df

        # Print the response structure for analysis
        print(f'Response structure for {symbol} - {statement_type}: {df}')

        # Get relevant dates from financial statements
        #relevant_dates = df['date'].tolist()  # Change 'df' to the appropriate DataFrame

        # Historical market capitalization data
        market_cap_pickle_filename = f'{pickle_dir}/{symbol}_historical_market_cap_data.pkl'

        try:
            # Try to load the DataFrame from the pickle file
            historical_market_cap_df = pd.read_pickle(market_cap_pickle_filename)
            print(f'Loaded historical market cap data for {symbol} from {market_cap_pickle_filename}')

        except FileNotFoundError:
            # If the pickle file is not found, make the API request and save the DataFrame to a pickle file
            # Modify the endpoint URL to include the relevant dates dynamically
            limit = 0 #this states the limit for the request below
            url_market_cap = f'{base_url}historical-market-capitalization/{symbol}?limit={limit}&apikey={api_key}'
            response_market_cap = requests.get(url_market_cap)

            if limit > 0: #start the process of retrieving data only if the limit is greater than 0 to avoid unnecessary API requests

                # Check if the request was successful (status code 200)
                if response_market_cap.status_code == 200:
                    # Parse the JSON response
                    market_cap_data = response_market_cap.json()

                    # Create a DataFrame from the response data
                    historical_market_cap_df = pd.DataFrame(market_cap_data)

                    # Save the DataFrame to a pickle file
                    historical_market_cap_df.to_pickle(market_cap_pickle_filename)
                    print(f'Saved historical market cap data for {symbol} to {market_cap_pickle_filename}')

                else:
                    # Print an error message if the request was not successful
                    print(
                        f'Error fetching historical market cap data for {symbol}. Status code: {response_market_cap.status_code}')

            elif limit == 0:
                print(f'Your limit for the requests on the historical market capitalization data is set to {limit}')

            else:
                print(f'Your limit for the API request for the historical market capitalization data is not specified or invalid. Limit: {limit}')
