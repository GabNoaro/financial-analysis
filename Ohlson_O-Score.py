"""
The Ohlson O-score for predicting bankruptcy is a multifactor financial formula postulated in 1980 by
Dr. James Ohlson of the New York University Stern Accounting Department as an alternative to the Altman Z-score
for predicting financial distress.

The Ohlson O-score is the result of a 9-factor linear combination of coefficient-weighted business ratios which are
readily obtained or derived from the standard periodic financial disclosure statements provided by publicly traded corporations.
Two of the factors utilized are widely considered to be dummies as their value and thus their impact upon the formula typically is 0.
When using an O-score to evaluate the probability of company’s failure, then exp(O-score) is divided by 1 + exp(O-score).

The original Z-score was estimated to be over 70% accurate with its later variants reaching as high as 90% accuracy.
The O-score is more accurate than this.

The range of the Ohlson O-Score is from -3 to +3. A higher score indicates a lower likelihood of bankruptcy,
while a lower score indicates a higher likelihood of bankruptcy.

The usual range for the Ohlson O-Score is between -0.5 and 1.5.
A score of 0.5 or higher suggests that the firm is unlikely to go bankrupt within the next two years.
A score of less than 0.5 suggests that the firm is more likely to go bankrupt within the next two years.

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

# Define the directory to store pickle files
pickle_dir = 'financial_data_pickle'
os.makedirs(pickle_dir, exist_ok=True)

# Define the type of financial statement (balance sheet, income statement, cash flow statement)
statement_types = ['balance-sheet-statement', 'income-statement', 'cash-flow-statement']

# Create dictionaries to hold data for each financial statement, symbol, and profile
balance_sheet_data = {}
income_statement_data = {}
cash_flow_statement_data = {}


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


# Define a function to calculate the Ohlson O-Score for a given symbol and financial statement data
def calculate_ohlson_oscore(symbol, balance_sheet, income_statement):
    # GNP (gross national product price index level)
    #gnp = 821.312 * (10 ^ 9)  # in USD bn for the UK # Input the Gross National Product (GNP) of the country of residency for the company compared
    # If the companies reside in differed countries, use the GNP of the US.

    # Get the year of the financial statement
    statement_year = pd.to_datetime(balance_sheet['date']).dt.year.max()

    # Manually input GNP values for each year
    gnp_values_uk = {
        2018: 2116600000000,
        2019: 2130400000000,
        2020: 2090700000000,
        2021: 2307700000000,
        2022: 2412200000000,
        2023: 2369300000000,
    }

    gnp_values_us = {
        2018: 21431000000000,
        2019: 22325000000000,
        2020: 20909000000000,
        2021: 23136000000000,
        2022: 25347000000000,
        2023: 25537000000000,
    }

    # Get the corresponding GNP value for the year
    gnp = gnp_values_uk.get(statement_year)

    if gnp is None:
        # Handle the case where GNP for the year is not available
        print(f"Warning: GNP value not available for the year {statement_year}.")

    # Check if all required data is available
    if balance_sheet.empty or income_statement.empty:
        print(f"Warning: Insufficient data for calculating O-Score for {symbol} in the year {statement_year}.")
        return np.nan  # Return NaN if data is insufficient

    # Get values from the financial statements and define the financial ratios used in the Ohlson O-Score
    net_income = income_statement['netIncome']
    total_assets = balance_sheet['totalAssets']
    #book_equity = balance_sheet['totalStockholdersEquity']
    #revenue = income_statement['revenue'] #get revenue or net sales
    working_capital = balance_sheet['totalCurrentAssets'] - balance_sheet['totalCurrentLiabilities']
    current_liabilities = balance_sheet['totalCurrentLiabilities']
    current_assets = balance_sheet['totalCurrentAssets']
    total_liabilities = balance_sheet['totalLiabilities']
    depreciation_and_amortization = income_statement['depreciationAndAmortization']
    gains_or_losses = income_statement['totalOtherIncomeExpensesNet']
    funds_from_operations = net_income + depreciation_and_amortization - gains_or_losses #FFO=Net Income+Depreciation+Amortization−Gains (or) + Losses
    last_year_net_income = net_income.shift(1)  # Assuming net income is a pandas Series or DataFrame column

    # Function to calculate X based on the criteria
    def calculate_x(total_liabilities, total_assets):
        return (total_liabilities > total_assets).astype(int)

    # Function to calculate Y based on the criteria
    def calculate_y(net_income):
        return 1 if net_income.iloc[-1] < 0 and net_income.iloc[-2] < 0 else 0

    # Calculate X and Y
    X = calculate_x(total_liabilities, total_assets)
    Y = calculate_y(net_income)

    # Calculate the Ohlson O-Score components
    ohlson_score = (-1.32 - 0.407 * np.log(total_assets / gnp)) + \
                   (6.03 * (total_liabilities / total_assets)) + \
                   (-1.43 * (working_capital / total_assets)) + \
                   (0.0757 * (current_liabilities / current_assets)) + \
                   (-1.72 * X) + \
                   (-2.37 * (net_income / total_assets)) + \
                   (-1.83 * (funds_from_operations / total_liabilities)) + \
                   (0.285 * Y) + \
                   (-0.521 * ((net_income - last_year_net_income) / (np.abs(net_income) + np.abs(last_year_net_income))))

    return ohlson_score


# Create a DataFrame to store the results
ohlscore_data = {'Symbol': [], 'Date/Period': [], 'Ohlson O-Score': []}

# Calculate and append the Ohlson O-Score for each company
for symbol in symbols:
    balance_sheet = balance_sheet_data.get(symbol, pd.DataFrame())
    income_statement = income_statement_data.get(symbol, pd.DataFrame())

    if not balance_sheet.empty and not income_statement.empty:
        ohlson_score = calculate_ohlson_oscore(symbol, balance_sheet, income_statement)

        # Append data to the results dictionary
        for i in range(len(ohlson_score)):
            ohlscore_data['Symbol'].append(symbol)
            ohlscore_data['Date/Period'].append(pd.to_datetime(balance_sheet['date'].iloc[i]))
            ohlscore_data['Ohlson O-Score'].append(ohlson_score[i])

# Create a DataFrame from the results dictionary
ohlscore_df = pd.DataFrame(ohlscore_data)

# Sort DataFrame by Date/Period in chronological order
ohlscore_df = ohlscore_df.sort_values(by='Date/Period')

# Save the DataFrame to a CSV file
ohlscore_df.to_csv(f'deliverables/ohlson_oscore_results_for_{symbols_str}.csv', index=False)

# Display the DataFrame
print("Ohlson O-Score DataFrame:")
print(ohlscore_df.to_string(index=False))

# Create a directory for deliverables if it doesn't exist
deliverables_dir = 'deliverables'
os.makedirs(deliverables_dir, exist_ok=True)

# Plotting the Ohlson O-Score
plt.figure(figsize=(10, 6))

for symbol in symbols:
    symbol_data = ohlscore_df[ohlscore_df['Symbol'] == symbol]
    plt.plot(symbol_data['Date/Period'], symbol_data['Ohlson O-Score'], label=symbol, marker='o', linestyle='-')

plt.xlabel('Date/Period')
plt.ylabel('Ohlson O-Score')
plt.title('Ohlson O-Score for Different Companies Over Time')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels by 45 degrees
plt.legend()
plt.tight_layout()

# Customize grid appearance
plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

# Set y-axis ticks starting from the minimum score to the maximum score with a step of 1
min_ohlson_score = ohlscore_df['Ohlson O-Score'].min()
max_ohlson_score = ohlscore_df['Ohlson O-Score'].max()
plt.yticks(np.arange(min_ohlson_score, max_ohlson_score + 1, 1))

# Draw stronger horizontal lines for integer y-axis ticks
for y_tick in np.arange(min_ohlson_score, max_ohlson_score + 1, 1.0):
    plt.axhline(y_tick, color='gray', linestyle='--', linewidth=1)

# Adjust legend position to avoid overlapping with lines
plt.legend(loc='upper left')

# Add a red line at Y = -1.78
plt.axhline(y=0.5, color='red', linestyle='--', linewidth=2, label='Threshold (0.5)')

# Save plot in the "deliverables" folder with symbols string in the name
symbols_str_no_comma = '_'.join(symbols)
plot_filename = os.path.join(deliverables_dir, f'Ohlson_O_Score_{symbols_str_no_comma}.png')
plt.savefig(plot_filename)

# Show plot
plt.show()