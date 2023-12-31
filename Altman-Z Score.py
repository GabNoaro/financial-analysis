"""
The Z-score formula for predicting bankruptcy was published in 1968 by Edward I.
Altman, who was, at the time, an Assistant Professor of Finance at New York University.
The formula may be used to predict the probability that a firm will go into bankruptcy within two years.
Z-scores are used to predict corporate defaults and an easy-to-calculate control measure for the financial distress
status of companies in academic studies.
The Z-score uses multiple corporate income and balance sheet values to measure the financial health of a company.
"""


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set Seaborn style
sns.set(style="whitegrid")

# Define the symbols for the selected tickers
symbols_str = 'CRM,ORCL,GOOGL,MSFT'
symbols = symbols_str.split(',')

industry = 'non_manufacturer' #you can specify between "manufacturer", "non_manufacturer", and "emerging_market"

# Define the directory to store pickle files
pickle_dir = 'financial_data_pickle'
os.makedirs(pickle_dir, exist_ok=True)

# Define the type of financial statement (balance sheet, income statement, cash flow statement)
statement_types = ['balance-sheet-statement', 'income-statement', 'cash-flow-statement']

# Create dictionaries to hold data for each financial statement, symbol, and profile
balance_sheet_data = {}
income_statement_data = {}
cash_flow_statement_data = {}
profile_data = {}  #Dictionary for profile data
historical_market_cap_data = {}  #Dictionary for historical market cap data


# Load profile data and historical market cap data for each symbol
for symbol in symbols:
    # Define the pickle file name for profile data
    profile_pickle_filename = f'{pickle_dir}/{symbol}_profile_data.pkl'
    market_cap_pickle_filename = f'{pickle_dir}/{symbol}_historical_market_cap_data.pkl'

    try:
        # Load the profile DataFrame from the pickle file
        profile_df = pd.read_pickle(profile_pickle_filename)
        historical_market_cap_df = pd.read_pickle(market_cap_pickle_filename)

        # Store the profile DataFrame and market cap DataFrame in the dictionaries
        profile_data[symbol] = profile_df
        historical_market_cap_data[symbol] = historical_market_cap_df

        print(f'Loaded profile data for {symbol} from {profile_pickle_filename}')
        print(f'Loaded historical market cap data for {symbol} from {market_cap_pickle_filename}')
        # uncomment the line below to inspect the market_cap df to find potential errors
        #historical_market_cap_df.to_csv(f'{pickle_dir}/{symbol}_historical_market_cap.csv')


    except FileNotFoundError:
        print(f'Profile pickle file not found: {profile_pickle_filename}')
        print(f'Market cap pickle file not found: {market_cap_pickle_filename}')

# Loop through each financial statement type
for symbol in symbols:
    for statement_type in statement_types:
        # Define the pickle file name
        pickle_filename = f'{pickle_dir}/{symbol}_{statement_type}_data.pkl'

        try:
            # Load the DataFrame from the pickle file
            df = pd.read_pickle(pickle_filename)

            # Store the DataFrame in the appropriate dictionary
            if statement_type == 'balance-sheet-statement':
                balance_sheet_data[symbol] = df
            elif statement_type == 'income-statement':
                income_statement_data[symbol] = df
            elif statement_type == 'cash-flow-statement':
                cash_flow_statement_data[symbol] = df

            print(f'Loaded {statement_type} data for {symbol} from {pickle_filename}')

        except FileNotFoundError:
            print(f'Pickle file not found: {pickle_filename}')



# Define a function to calculate the Altman Z-Score for a given symbol and financial statement data
def calculate_altman_zscore(symbol, balance_sheet, income_statement, industry='non_manufacturer'):
    # Get values from the financial statements and define the financial ratios used in the Altman Z-Score
    working_capital = balance_sheet['totalCurrentAssets'] - balance_sheet['totalCurrentLiabilities']
    retained_earnings = balance_sheet['retainedEarnings']
    earnings_before_interest_and_taxes = income_statement['operatingIncome']  # ebit
    # Assuming you have access to total assets and total liabilities
    total_assets = balance_sheet['totalAssets']  # Using the last available value
    total_liabilities = balance_sheet['totalLiabilities']  # Using the last available value
    revenue = income_statement['revenue'] #get revenue or net sales
    #market_cap = historical_market_cap_data['marketCap']  # get market cap

    # Calculate the market value of equity
    book_value_of_equity = total_assets - total_liabilities

    # Coefficients for different industries
    industry_coefficients = {
        'non_manufacturer': {'y1': 6.56, 'y2': 3.26, 'y3': 6.72, 'y4': 1.05, 'y5': 0, 'a': 0, 'z1': 2.6, 'z2': 1.1},
        'manufacturers': {'y1': 1.2, 'y2': 1.4, 'y3': 3.3, 'y4': 0.6, 'y5': 1, 'a': 0,  'z1': 2.99, 'z2': 1.81},
        'emerging_market': {'y1': 6.56, 'y2': 3.26, 'y3': 6.72, 'y4': 1.05, 'y5': 0, 'a': 3.25,  'z1': 2.6, 'z2': 1.1}
    }

    # Get coefficients for the specified industry
    #If the specified industry is not found, use the coefficients for 'non_manufacturer'
    coefficients = industry_coefficients.get(industry, industry_coefficients.get('non_manufacturer'))

    # Calculate the Altman Z-Score components
    if industry == 'manufacturing':
        z_score = coefficients['y1'] * (working_capital / total_assets) + \
                  coefficients['y2'] * (retained_earnings / total_assets) + \
                  coefficients['y3'] * (earnings_before_interest_and_taxes / total_assets) + \
                  coefficients['y4'] * (book_value_of_equity / total_liabilities) + \
                  coefficients['y5'] * (revenue / total_assets)
                  #need to substitute book value with market cap up here!!!
    else:
        z_score = coefficients['y1'] * (working_capital / total_assets) + \
                  coefficients['y2'] * (retained_earnings / total_assets) + \
                  coefficients['y3'] * (earnings_before_interest_and_taxes / total_assets) + \
                  coefficients['y4'] * (book_value_of_equity / total_liabilities) + \
                  coefficients['y5'] * (revenue / total_assets) + \
                  coefficients['a']

    return z_score

# Create a DataFrame to store the results
zscore_data = {'Symbol': [], 'Date/Period': [], 'Altman Z-Score': []}

# Calculate and append the Altman Z-Score for each company
for symbol in symbols:
    balance_sheet = balance_sheet_data.get(symbol, pd.DataFrame())
    income_statement = income_statement_data.get(symbol, pd.DataFrame())

    if not balance_sheet.empty and not income_statement.empty:
        z_score = calculate_altman_zscore(symbol, balance_sheet, income_statement)

        # Append data to the results dictionary
        for i in range(len(z_score)):
            zscore_data['Symbol'].append(symbol)
            zscore_data['Date/Period'].append(pd.to_datetime(balance_sheet['date'].iloc[i]))
            zscore_data['Altman Z-Score'].append(z_score[i])

# Create a DataFrame from the results dictionary
zscore_df = pd.DataFrame(zscore_data)

# Sort DataFrame by Date/Period in chronological order
zscore_df = zscore_df.sort_values(by='Date/Period')

# Save the DataFrame to a CSV file
zscore_df.to_csv(f'deliverables/altman_zscore_results_for_{symbols_str}.csv', index=False)

# Display the DataFrame
print("Altman Z-Score DataFrame:")
print(zscore_df.to_string(index=False))

# Create a directory for deliverables if it doesn't exist
deliverables_dir = 'deliverables'
os.makedirs(deliverables_dir, exist_ok=True)

# Plotting the Altman Z-Score
plt.figure(figsize=(10, 6))

for symbol in symbols:
    symbol_data = zscore_df[zscore_df['Symbol'] == symbol]
    plt.plot(symbol_data['Date/Period'], symbol_data['Altman Z-Score'], label=symbol, marker='o', linestyle='-')

    # Specify values for z1 and z2 based on the industry
    if industry == 'manufacturers':
        z1 = 2.99
        z2 = 1.81
    else:
        z1 = 2.6
        z2 = 1.1

    # Add lines for z1 and z2 values based on the industry
    plt.axhline(z1, color='g', linestyle='--', linewidth=2, label='_nolegend_')
    plt.axhline(z2, color='r', linestyle='--', linewidth=2, label='_nolegend_')

plt.xlabel('Date/Period')
plt.ylabel('Altman Z-Score')
plt.title('Altman Z-Score for Different Companies Over Time')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels by 45 degrees
plt.legend()
plt.tight_layout()

# Customize grid appearance
plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

# Set y-axis ticks starting from -0.5 and increasing by 0.5
plt.yticks(np.arange(-0.5, plt.ylim()[1] + 0.5, 0.5))

# Draw stronger horizontal lines for integer y-axis ticks
for y_tick in np.arange(-0.5, plt.ylim()[1] + 0.5, 1.0):
    plt.axhline(y_tick, color='gray', linestyle='--', linewidth=1)

# Adjust legend position to avoid overlapping with lines
plt.legend(loc='upper left')

# Save plot in the "deliverables" folder with symbols string in the name
symbols_str_no_comma = '_'.join(symbols)
plot_filename = os.path.join(deliverables_dir, f'Altman_Z_Score_{symbols_str_no_comma}.png')
plt.savefig(plot_filename)

# Show plot
plt.show()
