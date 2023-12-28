"""
The Beneish model is a statistical model that uses financial ratios calculated with accounting data of a specific
company in order to check if it is likely (high probability)
that the reported earnings of the company have been manipulated.

If M-score is less than -1.78, the company is unlikely to be a manipulator.
For example, an M-score value of -2.50 suggests a low likelihood of manipulation.
If M-score is greater than −1.78, the company is likely to be a manipulator.
For example, an M-score value of -1.50 suggests a high likelihood of manipulation.

"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set Seaborn style
sns.set(style="whitegrid")

# Define the symbols for the selected tickers
symbols_str = 'TSCO,MRK'
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


def calculate_beneish_mscore(symbol, income_statement, balance_sheet, cash_flow_statement):
    # Get values from the financial statements and define the financial ratios used in the Beneish M-Score

    net_income = income_statement['netIncome'].fillna(0)
    total_assets = balance_sheet['totalAssets'].fillna(0)
    cash_flow_from_operating_activities = cash_flow_statement['operatingCashFlow'].fillna(0)
    receivables = balance_sheet['netReceivables'].fillna(0)
    total_current_assets = balance_sheet['totalCurrentAssets'].fillna(0)
    total_current_liabilities = balance_sheet['totalCurrentLiabilities'].fillna(0)
    revenue = income_statement['revenue'].fillna(0)
    cost_of_goods_sold = income_statement['costOfRevenue'].fillna(0)
    depreciation = income_statement['depreciationAndAmortization'].fillna(0)
    sga_expenses = income_statement['sellingGeneralAndAdministrativeExpenses'].fillna(0)
    total_liabilities = balance_sheet['totalLiabilities'].fillna(0)
    #retained_earnings = balance_sheet['retainedEarnings'].fillna(0)
    pp_and_e = balance_sheet['propertyPlantEquipmentNet'].fillna(0)
    short_term_investments = balance_sheet['shortTermInvestments'].fillna(0)
    long_term_investments = balance_sheet['longTermInvestments'].fillna(0)

    securities = short_term_investments + long_term_investments


    def calculate_dsri(receivables, revenue):
        dsri = (receivables / revenue) / (receivables.shift(1) / revenue.shift(1))
        dsri = np.where(np.isinf(dsri), 0, dsri)
        return dsri.round(2)

    def calculate_gmi(revenue, cost_of_goods_sold):
        gmi = ((revenue.shift(1) - cost_of_goods_sold.shift(1)) / revenue.shift(1)) / \
                 ((revenue - cost_of_goods_sold) / revenue)
        gmi = np.where(np.isinf(gmi), 0, gmi)
        return gmi.round(2)

    def calculate_aqi(current_assets, pp_and_e, securities, total_assets):
        aqi = (1 - (current_assets + pp_and_e + securities) / total_assets) / \
                 (1 - (current_assets.shift(1) + pp_and_e.shift(1) + securities.shift(1)) / total_assets.shift(1))
        aqi = np.where(np.isinf(aqi), 0, aqi)
        return aqi.round(2)

    def calculate_sgi(revenue):
        sgi = revenue / revenue.shift(1)
        sgi = np.where(np.isinf(sgi), 0, sgi)
        return sgi.round(2)

    def calculate_depi(depreciation, pp_and_e):
        depi = (depreciation.shift(1) / (pp_and_e.shift(1) + depreciation.shift(1))) / \
                 (depreciation / (pp_and_e + depreciation))
        depi = np.where(np.isinf(depi), 0, depi)
        return depi.round(2)

    def calculate_sgai(sga_expenses, revenue):
        sgai = (sga_expenses / revenue) / (sga_expenses.shift(1) / revenue.shift(1))
        sgai = np.where(np.isinf(sgai), 0, sgai)
        return sgai.round(2)

    def calculate_lvgi(current_liabilities, total_long_term_debt, total_assets):
        lvgi = ((current_liabilities + total_long_term_debt) / total_assets) / \
                 ((current_liabilities.shift(1) + total_long_term_debt.shift(1)) / total_assets.shift(1))
        lvgi = np.where(np.isinf(lvgi), 0, lvgi)
        return lvgi.round(2)

    def calculate_tata(income_from_continuing_operations, cash_flows_from_operations, total_assets):
        tata = (income_from_continuing_operations - cash_flows_from_operations) / total_assets
        tata = np.where(np.isinf(tata), 0, tata)
        return tata.round(2)

    dsri = calculate_dsri(receivables, revenue)
    gmi = calculate_gmi(revenue, cost_of_goods_sold)
    aqi = calculate_aqi(total_current_assets, pp_and_e, securities, total_assets)
    sgi = calculate_sgi(revenue)
    depi = calculate_depi(depreciation, pp_and_e)
    sgai = calculate_sgai(sga_expenses, revenue)
    lvgi = calculate_lvgi(total_current_liabilities, total_liabilities, total_assets)
    tata = calculate_tata(net_income, cash_flow_from_operating_activities, total_assets)

    components = {
        'dsri': dsri,
        'gmi': gmi,
        'aqi': aqi,
        'sgi': sgi,
        'depi': depi,
        'sgai': sgai,
        'lvgi': lvgi,
        'tata': tata,
    }


    # Create a DataFrame
    components_df = pd.DataFrame(components).fillna(0).round(2)

    # Set Pandas display options to show all rows and columns
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # Print the DataFrame
    print(f'The components for {symbol} M-Score are{components_df}')

    def calculate_beneish_mscore(dsri, gmi, aqi, sgi, depi, sgai, lvgi, tata):
        return np.round((-4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi + 0.115 * depi - \
            0.172 * sgai + 4.679 * tata - 0.327 * lvgi), 2)

    # Now you can use this function to calculate the M-score
    m_score = calculate_beneish_mscore(dsri, gmi, aqi, sgi, depi, sgai, lvgi, tata).round(2)

    return m_score.round(2)

# Create a DataFrame to store the results
mscore_data = {'Symbol': [], 'Date/Period': [], 'Beneish M-Score': []}

# Calculate and append the Beneish M-Score for each company
for symbol in symbols:
    income_statement = income_statement_data.get(symbol, pd.DataFrame())
    balance_sheet = balance_sheet_data.get(symbol, pd.DataFrame())
    cash_flow_statement = cash_flow_statement_data.get(symbol, pd.DataFrame())

    if not income_statement.empty and not balance_sheet.empty and not cash_flow_statement.empty:
        m_score = calculate_beneish_mscore(symbol, income_statement, balance_sheet, cash_flow_statement)

        # Append data to the results dictionary
        for i in range(len(m_score)):
            mscore_data['Symbol'].append(symbol)
            mscore_data['Date/Period'].append(pd.to_datetime(income_statement['date'].iloc[i]))
            mscore_data['Beneish M-Score'].append(m_score[i])

# Create a DataFrame from the results dictionary
mscore_df = pd.DataFrame(mscore_data).fillna(0)
#mscore_df['Beneish M-Score'] = mscore_df['Beneish M-Score'].round(2)
mscore_df = np.round(mscore_df, 2)


# Sort DataFrame by Date/Period in chronological order
mscore_df = mscore_df.sort_values(by='Date/Period')

# Save the DataFrame to a CSV file
mscore_df.to_csv('beneish_mscore_results.csv', index=False)

# Display the DataFrame
print("Beneish M-Score DataFrame:")
print(mscore_df.to_string(index=False))


#Plot the results
# Replace infinite values with a large finite value
mscore_df.replace([np.inf, -np.inf], np.nan, inplace=True)

plt.figure(figsize=(10, 6))

for symbol in symbols:
    symbol_data = mscore_df[mscore_df['Symbol'] == symbol]
    plt.plot(symbol_data['Date/Period'], symbol_data['Beneish M-Score'], label=symbol, marker='o', linestyle='-')

plt.xlabel('Date/Period')
plt.ylabel('Beneish M-Score')
plt.title('Beneish M-Score for Different Companies Over Time')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels by 45 degrees
plt.legend()
plt.tight_layout()

# Customize grid appearance
plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

# Set y-axis ticks starting from the minimum score to the maximum score with a step of 1
min_beneish_score = mscore_df['Beneish M-Score'].min()
max_beneish_score = mscore_df['Beneish M-Score'].max()

# Round the min and max values to limit decimal places
min_beneish_score_rounded = round(min_beneish_score, 2)
max_beneish_score_rounded = round(max_beneish_score, 2)

# Check for finite values before setting yticks
if np.isfinite(min_beneish_score) and np.isfinite(max_beneish_score):
    plt.yticks(np.arange(min_beneish_score_rounded, max_beneish_score_rounded + 1, 1))

# Draw stronger horizontal lines for integer y-axis ticks
for y_tick in np.arange(min_beneish_score, max_beneish_score + 1, 1.0):
    plt.axhline(y_tick, color='gray', linestyle='--', linewidth=1)

# Add a red line at Y = -1.78
plt.axhline(y=-1.78, color='red', linestyle='--', linewidth=2, label='-1.78')
plt.axhline(y=0, color='yellow', linestyle='--', linewidth=2, label='0')

# Adjust legend position to avoid overlapping with lines
plt.legend(loc='upper left')

# Show plot
plt.show()
