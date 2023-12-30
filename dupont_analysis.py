import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math

# Set Seaborn style
sns.set(style="whitegrid")

# Define the symbols for the selected tickers
symbols_str = 'CRM,ORCL,GOOGL,MSFT'
symbols = symbols_str.split(',')

# Define the directory to store pickle files
pickle_dir = 'financial_data_pickle'
os.makedirs(pickle_dir, exist_ok=True)

# Define the type of financial statement (balance sheet, income statement, cash flow statement)
statement_types = ['balance-sheet-statement', 'income-statement']

# Create dictionaries to hold data for each financial statement, symbol, and profile
balance_sheet_data = {}
income_statement_data = {}


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

            print(f'Loaded {statement_type} data for {symbol} from {pickle_filename}')

        except FileNotFoundError:
            print(f'Pickle file not found: {pickle_filename}')

def calculate_dupont(symbol, income_statement, balance_sheet):
    # Get values from the financial statements and define the financial ratios used in the Beneish M-Score

    net_income = income_statement['netIncome'].fillna(0)
    revenue = income_statement['revenue'].fillna(0)
    ebitda = income_statement['ebitda'].fillna(0)
    ebt = income_statement['incomeBeforeTax'].fillna(0)
    depreciation_and_amortization = income_statement['depreciationAndAmortization'].fillna(0)
    interest_expense = income_statement['interestExpense'].fillna(0)
    total_assets = balance_sheet['totalAssets'].fillna(0)
    total_equity = balance_sheet['totalEquity'].fillna(0)
    ebit = ebt + interest_expense

    #Below you can find an alternative way to get EBIT and EBT, but the results are the same
    #You can uncomment the lines below if you want to double check EBT and EBIT
    #ebit2 = ebitda - depreciation_and_amortization
    #ebt2 = ebitda - depreciation_and_amortization - interest_expense
    #print(f"The ebit for {symbol} is {ebit}")
    #print(f"The ebit2 for {symbol} is {ebit2}")
    #print(f"The ebt for {symbol} is {ebt}")
    #print(f"The ebt2 for {symbol} is {ebt2}")

    # Calculate Dupont components
    tax_burden = net_income / ebt  # Tax Burden
    interest_burden = ebt / ebit  # Interest Burden
    operating_profit_margin = ebit / revenue  # Operating Profit Margin
    asset_turnover = revenue / total_assets  # Asset Turnover
    financial_leverage_ratio = total_assets / total_equity  # Financial Leverage Ratio

    # Calculate more granular components
    net_profit_margin = tax_burden * interest_burden * operating_profit_margin
    equity_turnover = asset_turnover * financial_leverage_ratio

    # Combine components into a DataFrame
    dupont_df = pd.DataFrame({
        'Date': pd.to_datetime(income_statement['date']),  # Convert 'date' to datetime format
        'Net Profit Margin': net_profit_margin,
        'Asset Turnover': asset_turnover,
        'Equity Turnover': equity_turnover,
        'Tax Burden': tax_burden,
        'Interest Burden': interest_burden,
        'Operating Profit Margin': operating_profit_margin,
        'Financial Leverage Ratio': financial_leverage_ratio
    })

    # Return the calculated values as a 1D array
    return [operating_profit_margin, tax_burden, interest_burden, asset_turnover, financial_leverage_ratio], dupont_df


# Check if there's only one symbol

if len(symbols) == 1:
    # Loop through symbols and plot individually
    for symbol in symbols:
        values, dupont_df = calculate_dupont(symbol, income_statement_data[symbol], balance_sheet_data[symbol])

        # Plot Dupont components
        plt.figure(figsize=(12, 6))
        plt.plot(dupont_df['Date'], dupont_df['Net Profit Margin'], label='Net Profit Margin', marker='o')
        plt.plot(dupont_df['Date'], dupont_df['Asset Turnover'], label='Asset Turnover', marker='x')
        plt.plot(dupont_df['Date'], dupont_df['Financial Leverage Ratio'], label='Financial Leverage Ratio', marker='x')

        plt.title(f'High Level Dupont Analysis for {symbol}')
        plt.xlabel('Date')
        plt.ylabel('Ratio')
        plt.legend()
        plt.show()

        # Plot Dupont granular components
        plt.figure(figsize=(12, 6))
        plt.plot(dupont_df['Date'], dupont_df['Tax Burden'], label='Tax Burden', marker='o')
        plt.plot(dupont_df['Date'], dupont_df['Interest Burden'], label='Interest Burden', marker='o')
        plt.plot(dupont_df['Date'], dupont_df['Operating Profit Margin'], label='Operating Profit Margin', marker='o')
        plt.plot(dupont_df['Date'], dupont_df['Asset Turnover'], label='Asset Turnover', marker='x')
        plt.plot(dupont_df['Date'], dupont_df['Financial Leverage Ratio'], label='Financial Leverage Ratio', marker='x')

        plt.title(f'Granular Dupont Analysis for {symbol}')
        plt.xlabel('Date')
        plt.ylabel('Ratio')
        plt.legend()
        plt.show()

        # Filter the DataFrame for the most recent year
        most_recent_year = dupont_df['Date'].dt.year.max()
        dupont_df_recent_year = dupont_df[dupont_df['Date'].dt.year == most_recent_year]

        # Extract values as NumPy arrays
        operating_profit_margin_r = dupont_df_recent_year['Operating Profit Margin'].values
        tax_burden_r = dupont_df_recent_year['Tax Burden'].values
        interest_burden_r = dupont_df_recent_year['Interest Burden'].values
        asset_turnover_r = dupont_df_recent_year['Asset Turnover'].values
        financial_leverage_ratio_r = dupont_df_recent_year['Financial Leverage Ratio'].values

        # Create a pie chart
        labels_pie = ['Operating Profit Margin', 'Tax Burden', 'Interest Burden', 'Asset Turnover',
                      'Financial Leverage Ratio']
        values_pie = [operating_profit_margin_r.sum(), tax_burden_r.sum(), interest_burden_r.sum(),
                      asset_turnover_r.sum(), financial_leverage_ratio_r.sum()]

        plt.figure(figsize=(8, 8))
        plt.pie(values_pie, labels=labels_pie, autopct='%1.1f%%', startangle=90)
        plt.title(f'Dupont Analysis for {symbol} - for year {most_recent_year}')
        plt.show()

else:
    # Create subplots for multiple symbols
    num_rows = math.ceil(len(symbols) / 2)
    num_cols = 2

    # Create subplots
    fig_components, axes_components = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))
    fig_granular, axes_granular = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))
    fig_pie, axes_pie = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))

    # Flatten the axes for ease of indexing
    axes_components = axes_components.flatten()
    axes_granular = axes_granular.flatten()
    axes_pie = axes_pie.flatten()

    # Initialize handles and labels variables outside the loop
    components_handles, components_labels = None, None
    granular_handles, granular_labels = None, None
    pie_handles, pie_labels = None, None

    labels_pie = ['Operating Profit Margin', 'Tax Burden', 'Interest Burden', 'Asset Turnover',
                  'Financial Leverage Ratio']

    # Loop through symbols and plot on subplots
    for i, symbol in enumerate(symbols):
        values, dupont_df = calculate_dupont(symbol, income_statement_data[symbol], balance_sheet_data[symbol])

        # Plot Dupont components
        components_plot = axes_components[i].plot(dupont_df['Date'], dupont_df['Net Profit Margin'],
                                                  label='Net Profit Margin', marker='o')
        axes_components[i].plot(dupont_df['Date'], dupont_df['Asset Turnover'], label='Asset Turnover', marker='x')
        axes_components[i].plot(dupont_df['Date'], dupont_df['Financial Leverage Ratio'],
                                label='Financial Leverage Ratio', marker='x')

        axes_components[i].set_title(f'High-level Dupont for {symbol}')
        axes_components[i].set_xlabel('Date')
        axes_components[i].set_ylabel('Ratio')

        # Plot Dupont granular components
        granular_plot = axes_granular[i].plot(dupont_df['Date'], dupont_df['Tax Burden'], label='Tax Burden',
                                              marker='o')
        axes_granular[i].plot(dupont_df['Date'], dupont_df['Interest Burden'], label='Interest Burden', marker='o')
        axes_granular[i].plot(dupont_df['Date'], dupont_df['Operating Profit Margin'], label='Operating Profit Margin',
                              marker='o')
        axes_granular[i].plot(dupont_df['Date'], dupont_df['Asset Turnover'], label='Asset Turnover', marker='x')
        axes_granular[i].plot(dupont_df['Date'], dupont_df['Financial Leverage Ratio'],
                              label='Financial Leverage Ratio', marker='x')

        axes_granular[i].set_title(f'Granular Dupont for {symbol}')
        axes_granular[i].set_xlabel('Date')
        axes_granular[i].set_ylabel('Ratio')

        # Filter the DataFrame for the most recent year
        most_recent_year = dupont_df['Date'].dt.year.max()
        dupont_df_recent_year = dupont_df[dupont_df['Date'].dt.year == most_recent_year]

        # Extract values as NumPy arrays
        operating_profit_margin_r = dupont_df_recent_year['Operating Profit Margin'].values
        tax_burden_r = dupont_df_recent_year['Tax Burden'].values
        interest_burden_r = dupont_df_recent_year['Interest Burden'].values
        asset_turnover_r = dupont_df_recent_year['Asset Turnover'].values
        financial_leverage_ratio_r = dupont_df_recent_year['Financial Leverage Ratio'].values

        # Create a pie chart
        values_pie = [operating_profit_margin_r.sum(), tax_burden_r.sum(), interest_burden_r.sum(),
                      asset_turnover_r.sum(), financial_leverage_ratio_r.sum()]

        # Create a pie chart
        axes_pie[i].pie(values_pie, labels=labels_pie, autopct='%1.1f%%', startangle=90)
        axes_pie[i].set_title(f'Dupont Analysis for {symbol} - for year {most_recent_year}')

        # Update handles and labels for pie chart legend
        if pie_handles is None:
            pie_handles, pie_labels = axes_pie[i].get_legend_handles_labels()
        else:
            pie_handles += axes_pie[i].get_legend_handles_labels()[0]

        # Update handles and labels for legends
        if components_handles is None:
            components_handles, components_labels = axes_components[i].get_legend_handles_labels()
            granular_handles, granular_labels = axes_granular[i].get_legend_handles_labels()
        else:
            components_handles += axes_components[i].get_legend_handles_labels()[0]
            granular_handles += axes_granular[i].get_legend_handles_labels()[0]

    # Create common legends outside of the loop
    fig_pie.legend(pie_handles, pie_labels, loc='lower right', bbox_to_anchor=(1, 0),
                   fancybox=True, shadow=True, ncol=5)
    fig_components.legend(components_handles, components_labels, loc='upper left', bbox_to_anchor=(0, 1),
                          fancybox=True, shadow=True, ncol=5)
    fig_granular.legend(granular_handles, granular_labels, loc='upper left', bbox_to_anchor=(0, 1),
                        fancybox=True, shadow=True, ncol=5)

    # Adjust layout for better spacing
    plt.tight_layout(pad=5)

    # Adjust the aspect ratio to shorten the y-axis for line charts
    #plt.subplots_adjust(wspace=0.1, hspace=0.9)  # Adjust the space between subplots

    # Show the figures
    plt.show()
