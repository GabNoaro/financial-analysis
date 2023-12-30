"""
Piotroski F-score is a number between 0 and 9 which is used to assess strength of company's financial position.
The score is used by financial investors in order to find the best value stocks (nine being the best).
The score is named after Stanford accounting professor Joseph Piotroski.
"""



import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

# Create dictionaries to hold data for each financial statement and symbol
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


# Define a function to calculate the Piotroski F-Score for a given symbol and financial statement data
def calculate_piotroski_fscore(symbol, balance_sheet, income_statement, cash_flow_statement):
    # Define the financial ratios used in the Piotroski F-Score
    net_income = income_statement['netIncome']
    roa = net_income / balance_sheet['totalAssets'].shift(1)
    operating_cash_flow = cash_flow_statement['operatingCashFlow']

    # Sum the preferredStock and commonStock to get totalShareOutstanding
    total_share_outstanding = (balance_sheet['preferredStock'] + balance_sheet['commonStock']).fillna(0)

    """
    # Calculate the Piotroski F-Score
    fscore = (
        (net_income > 0).astype(int) +
        (roa > 0).astype(int) +
        (net_income > 0).astype(int) +
        (operating_cash_flow > 0).astype(int) +
        (operating_cash_flow > net_income).astype(int) +
        (balance_sheet['longTermDebt'].diff() < 0).astype(int) +
        (roa.diff() > 0).astype(int) +
        (operating_cash_flow.diff() > 0).astype(int) +
        (total_share_outstanding.diff() <= 0).astype(int)
    )

    return fscore
    """

    # Calculate individual components of Piotroski F-Score first, so I can save and analyse them separately
    profitability = (net_income > 0).astype(int)
    operating_cash_flow_positive = (operating_cash_flow > 0).astype(int)
    change_in_roa = (roa.diff() > 0).astype(int)
    accruals = (operating_cash_flow > net_income).astype(int)
    change_in_leverage = (balance_sheet['longTermDebt'].diff() < 0).astype(int)
    change_in_liquidity = (roa.diff() > 0).astype(int)
    equity_issues = (total_share_outstanding.diff() <= 0).astype(int)
    change_in_gross_margin = (operating_cash_flow.diff() > 0).astype(int)
    change_in_asset_turnover = (net_income > 0).astype(int)

    # Calculate the Piotroski F-Score
    fscore = (
            profitability +
            operating_cash_flow_positive +
            change_in_roa +
            accruals +
            change_in_leverage +
            change_in_liquidity +
            equity_issues +
            change_in_gross_margin +
            change_in_asset_turnover
    )

    return fscore, {
        'Profitability': profitability,
        'Operating Cash Flow Positive': operating_cash_flow_positive,
        'Change in ROA': change_in_roa,
        'Accruals': accruals,
        'Change in Leverage': change_in_leverage,
        'Change in Liquidity': change_in_liquidity,
        'Equity Issues': equity_issues,
        'Change in Gross Margin': change_in_gross_margin,
        'Change in Asset Turnover': change_in_asset_turnover
    }

# Create a DataFrame to store the results
fscore_data = {'Symbol': [], 'Date/Period': [], 'Piotroski F-Score': []}
components_data = {'Symbol': [], 'Date/Period': [], 'Profitability': [],
                   'Operating Cash Flow Positive': [], 'Change in ROA': [],
                   'Accruals': [], 'Change in Leverage': [],
                   'Change in Liquidity': [], 'Equity Issues': [],
                   'Change in Gross Margin': [], 'Change in Asset Turnover': []}

# Calculate and append the Piotroski F-Score for each company
for symbol in symbols:
    balance_sheet = balance_sheet_data.get(symbol, pd.DataFrame())
    income_statement = income_statement_data.get(symbol, pd.DataFrame())
    cash_flow_statement = cash_flow_statement_data.get(symbol, pd.DataFrame())

    if not balance_sheet.empty and not income_statement.empty and not cash_flow_statement.empty:
        fscore, components = calculate_piotroski_fscore(symbol, balance_sheet, income_statement, cash_flow_statement)

        # Append data to the results dictionary
        for i in range(len(fscore)):
            fscore_data['Symbol'].append(symbol)
            fscore_data['Date/Period'].append(pd.to_datetime(income_statement['date'].iloc[i]))
            fscore_data['Piotroski F-Score'].append(fscore[i])

            # Append component scores
            components_data['Symbol'].append(symbol)
            components_data['Date/Period'].append(pd.to_datetime(income_statement['date'].iloc[i]))
            components_data['Profitability'].append(components['Profitability'][i])
            components_data['Operating Cash Flow Positive'].append(components['Operating Cash Flow Positive'][i])
            components_data['Change in ROA'].append(components['Change in ROA'][i])
            components_data['Accruals'].append(components['Accruals'][i])
            components_data['Change in Leverage'].append(components['Change in Leverage'][i])
            components_data['Change in Liquidity'].append(components['Change in Liquidity'][i])
            components_data['Equity Issues'].append(components['Equity Issues'][i])
            components_data['Change in Gross Margin'].append(components['Change in Gross Margin'][i])
            components_data['Change in Asset Turnover'].append(components['Change in Asset Turnover'][i])


# Create DataFrames from the results dictionaries
fscore_df = pd.DataFrame(fscore_data)
components_df = pd.DataFrame(components_data)

# Sort DataFrames by Date/Period in chronological order
fscore_df = fscore_df.sort_values(by='Date/Period')
components_df = components_df.sort_values(by='Date/Period')

# Save the DataFrames to CSV files
fscore_df.to_csv('piotroski_fscore_results.csv', index=False)
components_df.to_csv('piotroski_components_results.csv', index=False)

# Display the DataFrames
print("Piotroski F-Score DataFrame:")
print(fscore_df.to_string(index=False))

print("\nPiotroski Components DataFrame:")
print(components_df.to_string(index=False))


#PLOTTING THE F-SCORE
plt.figure(figsize=(10, 6))

for symbol in symbols:
    symbol_data = fscore_df[fscore_df['Symbol'] == symbol]
    plt.plot(symbol_data['Date/Period'], symbol_data['Piotroski F-Score'], label=symbol, marker='o', linestyle='-')

plt.xlabel('Date/Period')
plt.ylabel('Piotroski F-Score')
plt.title('Piotroski F-Score for Different Companies Over Time')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels by 45 degrees
plt.legend()
plt.tight_layout()

# Customize grid appearance
plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

# Show plot
plt.show()


#PLOTTING THE COMPONENTS
# Create a list of component names
component_names = ['Profitability', 'Operating Cash Flow Positive', 'Change in ROA',
                   'Accruals', 'Change in Leverage', 'Change in Liquidity',
                   'Equity Issues', 'Change in Gross Margin', 'Change in Asset Turnover']


# Create a grid of line charts for each component
fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(15, 4), sharey=True, sharex=True)  # Reduced height

for i, component in enumerate(component_names, 0):  # Start the index from 0
    row, col = divmod(i, 3)
    ax = axes[row, col]

    for symbol in symbols:
        symbol_data = components_df[components_df['Symbol'] == symbol]
        ax.plot(symbol_data['Date/Period'], symbol_data[component], label=symbol, marker='o', linestyle='-')

    ax.set_title(f'{component} Over Time')
    ax.set_xlabel('Date/Period')
    ax.set_ylabel('')
    ax.legend().set_visible(False)  # Hide legend in individual subplots

    # Rotate x-axis labels
    ax.tick_params(axis='x', rotation=60)

# Create a common legend outside the subplots
common_legend = fig.legend(labels=symbols, loc='upper left',
                           fancybox=True, shadow=True, ncol=len(symbols))

# Adjust the space between subplots, leave space on top for the common legend, and start a bit lower
plt.subplots_adjust(wspace=0.1, hspace=0.5, top=0.85, bottom=0.15)  # Adjust the bottom value

# Adjust layout to make room for the common legend
plt.tight_layout()

plt.show()
